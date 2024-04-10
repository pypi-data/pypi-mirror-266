# -*- coding: utf-8 -*- äöü vim: sw=4 sts=4 et tw=79
# Python compatibility:
from __future__ import absolute_import

from importlib_metadata import PackageNotFoundError, version

try:
    version('Products.LinguaPlone')
except PackageNotFoundError:
    class AlreadyTranslated(Exception):
        """
        Dummy exception; Products.LinguaPlone is not installed
        """
else:
    # Zope:
    from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated


class CantAddTranslationReference(AlreadyTranslated):
    """
    LinguaPlone has refused to add a translation reference,
    and we'd like to provide some more useful information
    """
    def __init__(self, o, canonical):
        AlreadyTranslated.__init__(self, o)
        try:
            o_lang = o.Language()
        except Exception as e:
            o_lang = e
        try:
            canonical_lang = canonical.Language()
        except Exception as e:
            canonical_lang = e
        self._raw_mapping = {
            'o': o,
            'o_lang': o_lang,
            'canonical': canonical,
            'canonical_lang': canonical_lang,
            'same_lang': o_lang == canonical_lang,
            'same_o': canonical is o,
            }

    def __str__(self):
        return ("CantAddTranslationReference(%(o)r,\n"
              """                            %(canonical)r):
        1st lang = %(o_lang)r, 2nd lang = %(canonical_lang)r
        (same language: %(same_lang)r; same object: %(same_o)r)
        """).strip() % self._raw_mapping

    def __repr__(self):
        return ("<CantAddTranslationReference(%(o)r, %(canonical)r)>"
                % self._raw_mapping)
