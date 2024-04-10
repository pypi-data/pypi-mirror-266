# -*- coding: utf-8 -*- äöü vim: ts=8 sts=4 sw=4 si et hls tw=79
# Python compatibility:
from __future__ import absolute_import


def _parse_init_options(kwdict, args):
    """
    Parse the options given during initialization

    We used to have 3 optional arguments which were normally specified
    positionally.  That's not ideal; optional arguments should better be given
    by name.  We don't enforce this yet, for compatibility reasons; but we like
    to have some testability.

    This function takes a dict of keyword arguments, and the tuple of
    positional arguments; it puts all information in that dict, which is
    changed in-place.

    >>> kw = {}
    >>> ar = ()
    >>> _parse_init_options(kw, ar)
    >>> sorted(kw.items())                     # doctest: +NORMALIZE_WHITESPACE
    [('forlist',    0),
     ('missing',    0),
     ('pretty',     0),
     ('searchtext', 0)]

    The values are just used as they are; we can use this to demonstrate the
    order of the traditional positional options:

    >>> kw.clear()
    >>> _parse_init_options(kw, (1, 2, 3))
    >>> sorted(kw.items())                     # doctest: +NORMALIZE_WHITESPACE
    [('forlist',    2),
     ('missing',    0),
     ('pretty',     1),
     ('searchtext', 3)]

    If missing=True, we'll need a missing_group_mask as well;
    we have a default value:

    >>> kw={'missing': 1}
    >>> _parse_init_options(kw, ar)
    >>> sorted(kw.items())                     # doctest: +NORMALIZE_WHITESPACE
    [('forlist',      0),
     ('missing',      1),
     ('missing_group_mask', 'Unknown or deleted group "{id}"'),
     ('pretty',       0),
     ('searchtext',   0)]

    Unknown keys yield TypeErrors, of course:
    >>> kw={'sillykey': 1}
    >>> _parse_init_options(kw, ar)
    Traceback (most recent call last):
      ...
    TypeError: Unsupported keyword option(s) ['sillykey']!

    """
    unsupported = set(kwdict) - set([
        'forlist',
        'missing',
        'pretty',
        'searchtext'])
    if unsupported:
        unsupported = sorted(unsupported)
        raise TypeError('Unsupported keyword option(s) %(unsupported)s!'
                        % locals())
    if isinstance(args, tuple):
        args = list(args)
    # these used to be accepted positionally:
    if 'pretty' not in kwdict:
        kwdict['pretty'] = (args.pop(0) if args
                            else 0)
    if 'forlist' not in kwdict:
        kwdict['forlist'] = (args.pop(0) if args
                             else 0)
    if 'searchtext' not in kwdict:
        kwdict['searchtext'] = (args.pop(0) if args
                                else 0)
    if args:
        if args[1:]:
            raise TypeError('Unsupported positional options %r (...)'
                            % tuple(args[:1]))
        else:
            raise TypeError('Unsupported positional option %(args)s'
                            % locals())
    # these are new:
    missing_mask_default = 'Unknown or deleted group "{group_id}"'
    missing_group_mask = kwdict.get('missing_group_mask')
    if 'missing' not in kwdict:
        missing = kwdict['missing'] = int(bool(missing_group_mask))
    else:
        missing = kwdict['missing']
    if missing and not missing_group_mask:
        kwdict['missing_group_mask'] = missing_mask_default


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
