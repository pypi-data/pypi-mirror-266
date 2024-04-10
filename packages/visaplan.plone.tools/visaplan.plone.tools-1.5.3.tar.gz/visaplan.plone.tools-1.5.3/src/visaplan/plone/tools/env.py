# -*- coding: utf-8 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""
visaplan.plone.tools.env: Information about the Zope environment
"""

# Python compatibility:
from __future__ import absolute_import

# Standard library:
from os import environ
from os.path import basename, curdir, normpath, sep

__all__ = [
    'worker_name',    # the name of the worker, e.g. 'instance' or 'client1'
    'var_directory',  # the 'var' directory path of the instance
    'lockfiles_directory',  # LOCKFILES_DIR, or {var}/lock
    ]


def worker_name(_env=None):
    """
    Return the name of the worker, e.g. 'client1'

    For long-running processes, e.g. upgrade steps, we might want to know the
    worker process which executes them; that way we are able to exclude that
    worker temporarily from the load balancing.

    We accept the `_env` option for testability,
    and for calls by the var_directory function (below).

    >>> e = dict(INSTANCE_HOME='/opt/zope/parts/instance')
    >>> worker_name(e)
    'instance'
    """
    if _env is None:
        _env = environ
    home = _env.get('INSTANCE_HOME')
    if home:
        worker = basename(home)
        return worker or None


def var_directory(_env=None, strict=0):
    """
    Return the (full) path to the "var" directory of the instance.

    Well; as we see it.  There might be a more reliable method to get this
    in a present or future Plone release; we might integrate it according to
    knowledge and (our) need.

    We accept the `_env` option for testability only.

    The CLIENT_HOME is always available, right?

    >>> e = dict(CLIENT_HOME='/opt/zope/instances/myplone/var/instance',
    ...        INSTANCE_HOME='/oh/whatever/parts/instance')
    >>> var_directory(e)
    '/opt/zope/instances/myplone/var'

    You might have configured a VAR_ROOT variable in your buildout,
    which will take precedence:
    >>> e.update({'VAR_ROOT': '/some/var/root/elsewhere'})
    >>> var_directory(e)
    '/some/var/root/elsewhere'

    What if the environment doesn't contain anything useful?
    >>> e=dict(junk='only')

    By default, we currently tolerate this and return None:
    >>> var_directory(e) is None
    True

    But if you prefer, you can be strict as well:
    >>> var_directory(e, strict=1)
    Traceback (most recent call last):
      ...
    KeyError

    Some corner case: The CLIENT_HOME contains the name of the instance binary
    only:
    >>> e = dict(CLIENT_HOME='instance',
    ...        INSTANCE_HOME='/oh/whatever/parts/instance')
    >>> var_directory(e) is curdir
    True
    """
    if _env is None:
        _env = environ
    val = _env.get('VAR_ROOT')
    if val:
        return val
    wn = worker_name(_env)
    val = _env.get('CLIENT_HOME')
    if val:
        liz = list(normpath(val).split(sep))
        if wn is not None:
            try:
                idx = liz.index(wn)
            except ValueError:
                pass
            else:
                del liz[idx:]
        if liz:
            return sep.join(liz)
        else:
            return curdir
    if strict:
        raise KeyError


def lockfiles_directory(_env=None, strict=0):
    """
    Return the (full) path to the directory to contain the lock files.

    This is aimed to contain lock files as created by zc.lockfile.LockFile,
    e.g. using our ConvenientLock wrapper class in the .lock module.

    We take into account, by precendence:

    1. A LOCKFILES_DIR environment variable, if present
    2. var_directory() + '/lock'

    We accept the `_env` option for testability only.

    >>> e = dict(CLIENT_HOME='/opt/zope/instances/myplone/var/instance',
    ...        INSTANCE_HOME='/oh/whatever/parts/instance')
    >>> lockfiles_directory(e)
    '/opt/zope/instances/myplone/var/lock'

    You might have configured a VAR_ROOT variable in your buildout,
    which will take precedence:
    >>> e.update({'VAR_ROOT': '/some/var/root/elsewhere'})
    >>> lockfiles_directory(e)
    '/some/var/root/elsewhere/lock'

    A LOCKFILES_DIR value, of course, will always win:
    >>> e.update({'LOCKFILES_DIR': '/i/want/cows'})
    >>> lockfiles_directory(e)
    '/i/want/cows'

    What if the environment doesn't contain anything useful?
    >>> e=dict(junk='only')

    By default, we currently tolerate this and return None:
    >>> lockfiles_directory(e) is None
    True

    But if you prefer, you can be strict as well:
    >>> lockfiles_directory(e, strict=1)
    Traceback (most recent call last):
      ...
    KeyError

    What if we don't have a LOCKFILES_DIR variable, and
    the CLIENT_HOME contains the name of the instance binary only?
    >>> e = dict(CLIENT_HOME='instance',
    ...        INSTANCE_HOME='/oh/whatever/parts/instance')
    >>> lockfiles_directory(e).startswith(curdir)
    True
    >>> lockfiles_directory(e)
    './lock'
    """
    if _env is None:
        _env = environ
    val = _env.get('LOCKFILES_DIR')
    if val:
        return val
    val = var_directory(_env, strict)
    if val:
        return sep.join([normpath(val), 'lock'])
    elif strict:
        raise KeyError


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
