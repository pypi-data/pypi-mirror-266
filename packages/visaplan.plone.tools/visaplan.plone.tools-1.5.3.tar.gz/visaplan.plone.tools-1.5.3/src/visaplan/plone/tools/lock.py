# -*- coding: utf-8 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""
visaplan.plone.tools.lock: Some sugar for zc.lockfile.LockFile

We depend on zc.lockfile in this module;
since you might not need it, we don't actually require that package in our metadata.

We add some sugar to the zc.lockfile.LockFile class, e.g. a context manager::

  form zc.lockfile import LockError
  from visaplan.plone.tools.lock import lock
  lfn = '/var/lock/perfectly-normal.lock'
  try:
      with lock(lfn):
          # do what you need to do ...
  except LockError as e:
      # by default, we won't catch that error

When leaving the context, we try to delete the lock file by default;
specify autodelete=False to prevent this.
We'll ignore any OSError which may occur during deletion, however;
if verbose (requires a logger to be specified), this will be logged.

Further remarks:

- The property ``filename`` provides the name used internally to create the
  zc.lockfile.LockFile;
- The property ``lockfile`` (not to be confused with the former) provides
  that very LockFile object.
- There is an ``acquire`` method you may use to get the lock,
  although the usual way will be to simply `__enter__` the context;
- there is a companion ``release`` method
  which is normally called by the ``__exit__`` method.

"""

# Python compatibility:
from __future__ import absolute_import, print_function

from importlib_metadata import PackageNotFoundError
from importlib_metadata import version as pkg_version

# Setup tools:
from packaging.version import parse as parse_version

# Standard library:
from os import unlink
from time import sleep

try:
    ZCLF_V = parse_version(pkg_version('zc.lockfile'))
except PackageNotFoundError:
    if __name__ == '__main__':
        ZCLF_V = parse_version('1.2.3.post4')
        print("Package zc.lockfile not found; some tests probably won't work!")
        class LockFile: pass
        class LockError(Exception): pass
    else:
        raise
else:
    # Zope:
    from zc.lockfile import LockError, LockFile

# Local imports:
from visaplan.plone.tools.env import worker_name

__all__ = [
    'ConvenientLock',  # our wrapper class, a context manager
    'lockfile_kwargs',  # build keyword args for zc.lockfile.LockFile creation
    ]

HAVE_CUSTOMCONTENT = ZCLF_V >= parse_version('1.2.0')  # 1.2.1+ recommended!
DEFAULTS_KW = {
    'add_pid': True,
    'add_hostname': False,
    'add_worker': False,
    'content_template': None,
    'sep': ';',
    }

def lockfile_kwargs(_zclf_v=None, _env=None, **kwargs):
    """
    Forge keyword arguments for zc.lockfile.LockFile;
    the first argument `name`, however, we expect to be specified positionally.

    Let's assume we have a recent zc.lockfile release,
    and we want the hostname to be included in the lockfile contents:

    >>> def lfkw_recent(**kw):
    ...     _zclf_v = parse_version('3.0.post1')
    ...     return lockfile_kwargs(_zclf_v, **kw)
    >>> lfkw_recent(add_hostname=1)
    {'content_template': '{pid};{hostname}'}

    If we have a pre-1.2.0 version, as pinned for Plone 4.3 versions by
    default, the content_template argument is not supported yet,
    so we'll get an empty dict:

    >>> def lfkw_ancient(**kw):
    ...     _zclf_v = parse_version('1.0.2')
    ...     return lockfile_kwargs(_zclf_v, **kw)
    >>> lfkw_ancient(add_hostname=1)
    {}

    In our Zope/Plone instances, we are sometimes interested in the "worker"
    (or part, in zc.buildout terms)
    which does certain things. We could look for the PID, of course,
    but the worker's name is much more "human readable";
    and since we just need to detect it once for each process ...

    We use the `.env.worker_name` for this purpose,
    which uses the environment, currently:

    >>> e = dict(INSTANCE_HOME='/opt/zope/parts/client3')
    >>> kw = {'add_worker': 1, '_env': e}
    >>> lfkw_recent(**kw)
    {'content_template': '{pid};client3'}

    Since there is no 'worker' support in zc.lockfile.LockFile,
    we simply use the value here.

    Now for some corner cases.

    Despite the fact that we "consume" the kwargs dict
    when processing the keyword arguments, it seems be be copied implicitly,
    so we can repeat our call and get the same result again:

    >>> lfkw_recent(**kw)
    {'content_template': '{pid};client3'}

    Arguments for the ConvenientLock class are not accepted here:
    >>> lfkw_recent(autodelete=1)
    Traceback (most recent call last):
      ...
    TypeError: Unsupported arguments!

    If the content_template is readily specified, we don't accept additional
    arguments, to avoid possible ambiguities.
    To avoid surprises, we fail for errors even if the zc.lockfile version
    doesn't support customized ocntent yet anyway:

    >>> lfkw_ancient(add_hostname=1, content_template='{pid}')
    Traceback (most recent call last):
      ...
    TypeError: With content_template given, no other arguments are allowed!

    """
    pop = kwargs.pop
    if _zclf_v is None:
        _zclf_v = ZCLF_V
    have_customcontent = _zclf_v > parse_version('1.2.0')

    _ct = pop('content_template', None)
    if _ct is not None:
        if kwargs:
            raise TypeError('With content_template given, no other arguments '
                            'are allowed!')
        elif have_customcontent:
            return {'content_template': _ct}
        else:
            return {}
    sep = pop('sep', ';')
    added = [key[4:] for key in DEFAULTS_KW.keys()
             if key.startswith('add_') and pop(key, DEFAULTS_KW[key])
             ]
    if kwargs:
        raise TypeError('Unsupported arguments!')
    if added == ['pid'] or not have_customcontent:
        # this is the default:
        return {}
    res = [key.join('{}') for key in ['pid', 'hostname']
           if key in added]
    if 'worker' in added:
        w = worker_name(_env)
        if w:
            res.append(w)
    return {'content_template': sep.join(res)}


class ConvenientLock(object):
    """
    A convience wrapper for zc.lockfile.LockFile
    """

    def __init__(self, name, **kwargs):
        self.__filename = name
        self.__lockfile = None
        pop = kwargs.pop
        self.__autodelete = pop('autodelete', 1)
        self._tries = tries = pop('tries', 1)
        if tries > 1:
            if 'delay' not in kwargs:
                raise TypeError('With tries=%(tries)r, we demand a delay value!'
                                % locals())
            self._delay = delay = pop('delay')
            if not isinstance(delay, (int, float)):
                raise ValueError('Number expected; found %s' % (type(delay),))
            elif delay <= 0:
                raise ValueError('Number [seconds] > 0 expected; found %r'
                                 % (delay,
                                    ))
        self._logger = logger = pop('logger', None)
        self._verbose = verbose = pop('verbose',
                              1 if logger is not None
                              else 0)
        if verbose and not logger:
            raise TypeError("Can't be verbose with no logger given!")
        self._lfkw = lockfile_kwargs(**kwargs)

    def __enter__(self):
        if not self.active:
            self.acquire()

    def acquire(self):
        i = 1
        tries = self._tries
        if tries > 1:
            delay = self._delay
        verbose = self._verbose
        if verbose:
            logger = self._logger
        filename = self.__filename
        while True:
            try:
                self.__lockfile = LockFile(filename, **self._lfkw)
            except LockError as e:
                if verbose:
                    msg = str(e)
                if i < tries:
                    i += 1
                    if verbose:
                        # (verified syntax:)
                        logger.warn('%s: sleep %f seconds, then retry ...',
                                    msg, delay)
                    sleep(delay)
                else:
                    if verbose:
                        logger.error(msg)
                    raise
            else:
                if verbose >= 2:
                    logger.info('Acquired lock: %r', self)
                break

    def __repr__(self):
        return "<%s('%s'): %s>" % (
                self.__class__.__name__,
                self.__filename,
                self.status,
                )

    @property
    def status(self):
        if self.active:
            return 'ACTIVE'
        elif self.__lockfile is None:
            return 'UNINITIALIZED'
        else:
            fp = self.__lockfile._fp
            if fp is None:
                return 'CLOSED'
            elif fp.closed:
                return 'closed'
            else:
                return '???'

    @property
    def lockfile(self):
        """
        This is the zc.lockfile.LockFile instance which we use internally
        """
        return self.__lockfile

    @property
    def filename(self):
        """
        This is the filename used to create the zc.lockfile.LockFile instance
        """
        return self.__filename

    @property
    def active(self):
        _lf = self.__lockfile
        if _lf is None:
            return False
        _fp = _lf._fp
        if _fp is None:
            return False
        return not _fp.closed

    def release(self):
        if self.active:
            self.__lockfile.close()
        verbose = self._verbose
        if verbose >= 1:
            logger = self._logger
        if self.__autodelete:
            filename = self.__filename
            try:
                unlink(filename)
            except OSError as e:
                if verbose:
                    logger.warn("LockFile %(filename)r NOT deleted!",
                                      locals())
            else:
                if verbose >= 2:
                    logger.info('Lockfile %(filename)r deleted!',
                                      locals())
        elif verbose >= 2:
            logger.info('Lockfile %r left behind.', self.__filename)
        if verbose >= 3:
            logger.info('Left context of %r', self)

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
