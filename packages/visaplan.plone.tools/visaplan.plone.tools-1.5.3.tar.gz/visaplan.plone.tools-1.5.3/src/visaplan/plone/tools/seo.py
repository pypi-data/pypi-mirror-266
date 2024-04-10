"""
SEO helpers;
for now, supporting structured data, see:

https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
https://schema.org
"""

# see as well (gf):
# ../../../../../../visaplan.plone.animations/src/visaplan/plone/animations/utils/_lapa.py
# ../../../../../../visaplan.plone.elearning/src/visaplan/plone/elearning/utils/_lapa.py

# Python compatibility:
from __future__ import absolute_import

# Standard library:
from re import match

__all__ = [
    'parse_title',  # ... course, lesson titles
    ]

_LD_CONTEXT = 'https://schema.org'
# -------------------------------- [ regular expression snippets ... [
_RE_START_ANCHOR = (
   u'(?i'      # ignore case (like flags=re.IGNORECASE)
     u'm)'     # multi-line  (like    ...re.MULTILINE)
   u'\\A')     # beginning of the string

_RE_CODE_GROUP = (
    u'(?P<courseCode>'
    u'\\b[A-Z]+'
    u'-'
    u'[0-9]+)'
    u'\\b'
    u' *')
_RE_NAME = (
    u'(?P<name>'
    u'\\b[A-Z].*[A-Za-z)]'
    u')'
    )
_RE_VERSION = (
    u' *- *v[0-9]+\\b'
    )
_RE_FREE = (
    u' *- *[Ff][Rr][Ee][EeIi][!]?'
    )

_RE_END_ANCHOR = u'\\Z'
_RE_END = u' *' + _RE_END_ANCHOR
# -------------------------------- ] ... regular expression snippets ]

RE_LIST = [
    # ----------------------------- [ titles with "course codes" ... [
    # (which we have in lesson titles as well!)
    # title with a version, and optionally "FREE!"
    _RE_START_ANCHOR +
    _RE_CODE_GROUP +
    _RE_NAME +
    _RE_VERSION +
    u'(?:' + _RE_FREE + u')?' +
    _RE_END,
    # title with "FREE!" and perhaps a version:
    _RE_START_ANCHOR +
    _RE_CODE_GROUP +
    _RE_NAME +
    _RE_FREE +
    u'(?:' + _RE_VERSION + u')?' +
    _RE_END,
    # title without known suffixes:
    _RE_START_ANCHOR +
    _RE_CODE_GROUP +
    _RE_NAME +
    _RE_END,
    # ----------------------------- ] ... titles with "course codes" ]

    # ------------- [ the same for titles *WITHOUT* course codes ... [
    # title with a version, and optionally "FREE!"
    _RE_START_ANCHOR +
    _RE_NAME +
    _RE_VERSION +
    u'(?:' + _RE_FREE + u')?' +
    _RE_END,
    # title with "FREE!" and perhaps a version:
    _RE_START_ANCHOR +
    _RE_NAME +
    _RE_FREE +
    u'(?:' + _RE_VERSION + u')?' +
    _RE_END,
    # title without known suffixes:
    _RE_START_ANCHOR +
    _RE_NAME +
    _RE_END,
    # ------------- ] ... the same for titles *WITHOUT* course codes ]
    ]


def parse_title(title, stype=None):
    """
    Parse a given (course, lesson ...) title and return a dict;
    the group names resemble properties for structured types as of schema.org.

    We'll use a little test helper:
    >>> def pt(*args, **kw):
    ...     return sorted(parse_title(*args, **kw).items())

    Our course objects have often a name prefix which resembles a courseCode:

    >>> pt('BE-50 Trench Protection and Pipe Installation - v01')
    ...                # doctest: +NORMALIZE_WHITESPACE
    [(u'courseCode', 'BE-50'),
     (u'name',       'Trench Protection and Pipe Installation')]

    We only return data which we consider useful for structured data use;
    the "- v01" suffix is silently dropped.
    This happens implicitly, since we don't but it in a match group.

    We can use this function to initialize structured data for the respective
    object.
    Let's specify a type:

    >>> pt('BE-50 Trench Protection and Pipe Installation - v01',
    ...    'Course')                   # doctest: +NORMALIZE_WHITESPACE
    [('@context',    'https://schema.org'),
     ('@type',       'Course'),
     (u'courseCode', 'BE-50'),
     (u'name',       'Trench Protection and Pipe Installation')]

    What if we have a lesson here, rather than a course?
    The courseCode wouldn't be valid, so we drop it:

    >>> pt('BE-50 Trench Protection and Pipe Installation - v01',
    ...    'LearningResource')         # doctest: +NORMALIZE_WHITESPACE
    [('@context',    'https://schema.org'),
     ('@type',       'LearningResource'),
     (u'name',       'Trench Protection and Pipe Installation')]

    What if we specify some really unexpected crap?
    At the very least, we return a 'name', with surrounding whitespace
    stripped:

    >>> pt(' (oh such crap!) ')
    [('name', '(oh such crap!)')]

    """
    drop_keys = set()
    if stype:
        res = {
            '@context': _LD_CONTEXT,
            '@type':    stype,
            }
        if stype != 'Course':
            drop_keys.add('courseCode')
    else:
        res = {}
    for re in RE_LIST:
        m = match(re, title)
        if m is not None:
            res.update(m.groupdict())
            break
    if drop_keys:
        for key in res.keys():
            if key in drop_keys:
                del res[key]
    if not res.get('name'):
        res['name'] = title.strip()

    return res


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
