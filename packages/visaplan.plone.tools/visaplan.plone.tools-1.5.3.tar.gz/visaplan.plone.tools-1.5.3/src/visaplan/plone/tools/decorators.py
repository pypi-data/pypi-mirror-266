# -*- coding: utf-8 -*-
# Python compatibility:
from __future__ import absolute_import

from importlib_metadata import PackageNotFoundError
from importlib_metadata import version as pkg_version

# Standard library:
from functools import wraps

try:
    pkg_version('simplejson')
except PackageNotFoundError:
    # Standard library:
    from json import dumps
else:
    # 3rd party:
    from simplejson import dumps


def returns_json(raw):
    """
    Decorate the given function to ...
    - convert the result to JSON,
      and
    - add the appropriate HTTP headers

    This is for JSON data requested by a client ("TTW");
    DON'T apply it to functions which are used in a view to build other contents
    around it, as the HTTP headers will be incorrect;
    the user agent might try to parse your HTML page as JSON and fail.

    For this purpose, see the @headless_json decorator (below).
    """
    @wraps(raw)
    def wrapped(self, **kwargs):
        dic = raw(self, **kwargs)
        txt = dumps(dic)
        context = self.context
        setHeader = context.REQUEST.RESPONSE.setHeader
        setHeader('Content-Type', 'application/json; charset=utf-8')
        setHeader('Content-Length', len(txt))
        return txt
    return wrapped


def headless_json(raw):
    """
    Decorate the given function to convert the result to JSON. Period.

    This is for JSON data used internally;
    for public views which serve data to Javascript code you'll prefer
    the @returns_json decorator (above).

    >>> @headless_json
    ... def f(): return dict(eins=2, drei='vier')
    >>> f()
    '{"drei": "vier", "eins": 2}'
    """
    @wraps(raw)
    def wrapped(*args, **kwargs):
        dic = raw(*args, **kwargs)
        txt = dumps(dic)
        return txt
    return wrapped


if __name__ == '__main__':
   import doctest
   doctest.testmod()
