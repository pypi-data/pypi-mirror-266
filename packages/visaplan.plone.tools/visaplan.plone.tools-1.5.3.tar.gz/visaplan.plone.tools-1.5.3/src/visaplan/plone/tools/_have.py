# detect optional packages

# Python compatibility:
from __future__ import absolute_import

from importlib_metadata import PackageNotFoundError, version

try:
    version('beautifulsoup4')
except PackageNotFoundError:
    HAS_BEAUTIFULSOUP = False
else:
    HAS_BEAUTIFULSOUP = True

try:
    version('plone.app.blob')
except PackageNotFoundError:
    HAS_BLOB = False
else:
    HAS_BLOB = True

try:
    version('plone.dexterity')
except PackageNotFoundError:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True

try:
    version('Products.Archetypes')
except PackageNotFoundError:
    HAS_ARCHETYPES = False
else:
    HAS_ARCHETYPES = True

try:
    version('visaplan.kitchen')
except PackageNotFoundError:
    HAS_KITCHEN = False
else:
    HAS_KITCHEN = True

try:
    version('visaplan.plone.infohubs')
except PackageNotFoundError:
    HAS_INFOHUBS = False
else:
    HAS_INFOHUBS = True

try:
    version('visaplan.plone.subportals')
except PackageNotFoundError:
    HAS_SUBPORTALS = False
else:
    HAS_SUBPORTALS = True

try:
    version('visaplan.plone.search')
except PackageNotFoundError:
    HAS_VPSEARCH = False
else:
    HAS_VPSEARCH = True

try:
    version('zope.i18n')
except PackageNotFoundError:
    HAS_ZOPE_I18N = False
else:
    HAS_ZOPE_I18N = True
