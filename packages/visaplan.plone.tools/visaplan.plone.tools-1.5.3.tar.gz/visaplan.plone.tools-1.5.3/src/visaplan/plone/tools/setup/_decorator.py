# -*- coding: utf-8 -*- äöü vim: sw=4 sts=4 et tw=79
"""
Decorators for GenericSetup upgrade steps and handler functions

Common functionality of the decorators provided by this module:

- They expect the decorated function to accept a context and a logger argument.
  The logger argument might be omitted depending on the usage, so it is
  complemented by the decorator for this cases;
  thus, the decorated function doesn't need any code to handle a missing logger option.

- They use the given or created logger to log the time it took to run the function.

- They catch the KeyboardInterrupt to allow the function to be aborted but not
  abort the foreground Zope process (which will receive a special StepAborted
  exception in this case);
  all other exceptions are logged (including the time the function ran up to
  this point) and re-raised.
"""

# Python compatibility:
from __future__ import absolute_import

# Standard library:
from functools import wraps
from time import time

# Local imports:
from visaplan.plone.tools.env import worker_name

# Logging / Debugging:
import logging

__all__ = [
        # decorators:
        'upgradeStep',  # inject a default logger (deprecated name: 'step')
        'installStep',  # check for a marker file (deprecated name: 'importStep')
        # noch unfertig:
        # 'upgradeTo',
        'make_step_decorator',
        # exceptions:
        'StepAborted',
        ]


class StepAborted(Exception):
    """
    Vom Dekorator @upgradeStep geworfen, wenn in einem Migrationsschritt eine
    KeyBoard-Exception ausgelöst wurde
    """


def upgradeStep(func):
    """
    Dekorator für Migrationsschritte:
    - ergänzt ein ggf. fehlendes logger-Argument
      und
    - verwendet dabei den Namen des Workers
    - stoppt die Zeit
    - (experimentell:)
      erlaubt das Weiterlaufen der Zope-Instanz auch nach manuellem Abbruch
      des Migrationsschritts
    """
    # da die def-Anweisung hier nicht ausgeführt wird, ist eine implizite
    # "Impfung" der verpackten Funktion mit zusätzlichen Variablen (wie z.B.
    # "site") leider nicht möglich; dafür würden zusätzliche Argumente
    # benötigt, und mithin eine Änderung der Signatur.

    @wraps(func)
    def wrapper(context, logger=None):
        funcname = func.__name__
        if logger is None:
            label = ':'.join([_f for _f in [
                                    'setup',
                                    worker_name(),
                                    funcname,
                                    ] if _f])
            logger = logging.getLogger(label)
        _started = time()
        try:
            res = func(context, logger)
        except Exception as e:
            delta = time() - _started
            if isinstance(e, KeyboardInterrupt):
                logger.error('%(funcname)s aborted after %(delta)5.2f seconds',
                             locals())
                logger.exception(e)
                raise StepAborted
            else:
                logger.error('%(funcname)s: %(e)r after %(delta)5.2f seconds',
                             locals())
                logger.exception(e)
                raise
        else:
            delta = time() - _started
            logger.info('%(res)r <-- %(funcname)s (%(delta)5.2f seconds)', locals())
        return res

    return wrapper


def installStep(marker_file, verbose=False):
    """
    Return a decorator for functions which are constrained by a marker file:
    the decorated function will be executed *only* if the given file is found.

    Options:

      marker_file -- relative path to a marker file (required)

             Note: This path is not (yet?) checked for existence,
                   but this might change in a future release!

      verbose -- enables some informational output (default: False)

    Some .setuphandlers functions are commonly executed in the context of their
    own package only and thus usually start with something like::

      >>> if context.readDataFile('my.astonishing.addon-marker.txt') is None:
      ...    return                   # doctest: +SKIP

    The file in question is commonly located in some local directory
    in the package sources ('profiles/default/') relative to the module.

    For convenience, we provide a decorator which allows you to write things
    like::

      >>> @installStep('profiles/default/my.astonishing.addon-marker.txt')
      ... def setup_various(context):
      ...     portal = context.getSite()
      ...     do_fancy_things(portal)  # doctest: +SKIP

    That way you see the path to that file; but as the readDataFile method
    expects the filename only, it is shortened.

    To prevent errors, the installStep won't accept anything callable by itself:

    >>> def some_function(context): pass
    >>> installStep(some_function)   # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: This function doesn't decorate any function directly
               but expects the name of a marker file and
               *returns* the decorator!

    We *always* want our installSteps to check a marker file, right?!
    (If not, you wouldn't use our decorator -- if any at all!)
    >>> installStep()   # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: installStep() takes at least 1 argument (0 given)

    Other wrong usage should be prevented as well:
    >>> installStep(None)   # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: Please specify the name of a marker file!
    >>> installStep(0)   # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    AttributeError: 'int' object has no attribute 'split'

    """
    if marker_file is None:
        raise ValueError('Please specify the name of a marker file!')
    elif callable(marker_file):
        raise TypeError('This function doesn\'t decorate any function directly'
            ' but expects the name of a marker file'
            ' and *returns* the decorator!')

    fn = marker_file.split('/')[-1]

    def my_decorator(f):
        if verbose:
            print('*** decorating %r: check for marker file %r' % (f, fn))
        @wraps(f)
        def wrapper(context, *args, **kwargs):
            if verbose:
                print('*** Check context %r for file %s ...' % (context, fn))
            if context.readDataFile(fn) is None:
                return
            if verbose:
                print('*** Now executing %r ...' % f)
            try:
                return f(context, *args, **kwargs)
            except KeyboardInterrupt:
                raise StepAborted

        return wrapper

    return my_decorator


def upgradeTo(destination, **kwargs):
    """
    Gib einen Dekorator zur einmaligen Verwendung zurück.
    Es wird als erstes Argument die Zielversion (destination)
    angegeben; weitere werden üblicherweise in einem Dict gesammelt:

    >>> deco_kwargs = {'package': __package__, 'module': __name__}
    >>> @upgradeTo(1001, **deco_kwargs)  # doctest: +SKIP
    ... def create_interesting_folder(context, logger):
    ...     pass

    Der Dekorator sorgt für das (je nach Aufruf fehlende) logger-Argument;
    protokolliert wird:
    - die Zielversion (destination)
    - der Name der Funktion
    - jeweils wenn übergeben:
      - der Name des Python-Packages (package)
      - der Name des Moduls (module)
      - die Revisionsnummer (rev), normalerweise als String

    Die Logik ist wie folgt:
    - upgradeTo wird aufgerufen und verarbeitet die übergebenen Argumente,
      um eine Funktion mit einem Argument <func> zu erzeugen,
      die die übergebene Funktion dekoriert
    - die so generierte Funktion bekommt die letztlich zu dekorierende Funktion
      übergeben und gibt eine Wrapper-Funktion zurück, die folgendes tut:
      - sie erzeugt einen Logger, falls nicht übergeben,
        und ergänzt so das an die dekorierte Funktion übergebene logger-Argument;
      - sie protokolliert das Paket (sofern package übergeben; dringend
        empfohlen!) und die Zielversion
      - sie protokolliert den Namen der dekorierten Funktion
      - sie ruft die dekorierte Funktion auf und merkt sich den Zeitpunkt
      - sie protokolliert den Rückgabewert und die Brutto-Laufzeit der
        dekorierten Funktion
        - im Fehlerfall werden entsprechende Informationen protokolliert
      - schließlich nochmals ein Protokolleintrag für das Paket und die
        Zielversion
    """

    def make_wrapper():
        """
        package = package
        destination = destination
        rev = rev
        """
        rev = kwargs.pop('rev', 0)
        package = kwargs.pop('package')
        module = kwargs.pop('module', None)
        logger = kwargs.pop('logger', None)
        logger_name = kwargs.pop('logger_name', 'setup:%(funcname)s')

        @wraps(func)
        def wrapper(context, logger=logger):
            funcname = func.__name__
            package = package
            destination = destination
            rev = rev
            if logger is None:
                logger = logging.getLogger(logger_name % locals())
            logger.info('[ updating %(package)s to version %(destination)s ... [',
                        locals())
            '''
                        {'package': package,
                         'destination': destination,
                        })
            '''
            _started = time()
            if rev:
                logger.info('%(funcname)s@%(rev)s started', locals())
            else:
                logger.info('%(funcname)s started', locals())
            try:
                res = func(context, logger)
            except Exception as e:
                delta = time() - _started
                if isinstance(e, KeyboardInterrupt):
                    logger.error('%(funcname)s aborted after %(delta)5.2f seconds',
                                 locals())
                    logger.exception(e)
                    logger.error('] ... update of %(package)s to version'
                                 ' %(destination)s aborted ]',
                                 locals())
                    raise StepAborted
                else:
                    logger.error('%(funcname)s: %(e)r after %(delta)5.2f seconds',
                                 locals())
                    logger.exception(e)
                    logger.error('] ... update of %(package)s to version'
                                 ' %(destination)s failed ]',
                                 locals())
                    raise
            else:
                delta = time() - _started
                logger.info('%(funcname)s completed (%(delta)5.2f seconds)', locals())
                logger.info('] ... %(package)s updated to version %(destination)s ]',
                            locals())
            return res

        return wrapper
    return make_wrapper()


def make_step_decorator(**kwargs):
    """
    Erzeuge einen Dekorator wie vorstehende Funktion --> upgradeStep,
    aber ergänze bei der Protokollierung des Aufrufs, gemäß benannten
    Argumenten:
    - rev --> die svn-Revision des aufrufenden Moduls;
      z. B., wenn das svn:keyword "Revision" aktiv ist:
      >>> MODULE_REVISION = '$Revision: 31126 $'[8+3:-2]
    """
    rev = kwargs.pop('rev', 0)
    mask = 'setup:%(funcname)s'
    if rev:
        int(rev)
        mask += '@' + rev

    def make_wrapper(func, rev=rev):
        @wraps(func)
        def wrapper(context, logger=None):
            funcname = func.__name__
            rev = rev
            if logger is None:
                logger = logging.getLogger('setup:'+funcname)
            _started = time()
            if rev:
                logger.info('%(funcname)s@%(rev)s started', locals())
            try:
                res = func(context, logger)
            except Exception as e:
                delta = time() - _started
                if isinstance(e, KeyboardInterrupt):
                    logger.error('%(funcname)s aborted after %(delta)5.2f seconds',
                                 locals())
                    logger.exception(e)
                    raise StepAborted
                else:
                    logger.error('%(funcname)s: %(e)r after %(delta)5.2f seconds',
                                 locals())
                    logger.exception(e)
                    raise
            else:
                delta = time() - _started
                logger.info('%(funcname)s completed (%(delta)5.2f seconds)', locals())
            return res

        return wrapper
    return make_wrapper

if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
