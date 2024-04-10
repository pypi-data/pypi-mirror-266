# Python compatibility:
from __future__ import absolute_import

from importlib_metadata import PackageNotFoundError, version

# Setup tools:
from packaging.version import parse as parse_version

try:
    _vps_v = version('visaplan.plone.search')
except PackageNotFoundError:
    getExcludeFromNav = 'exclude_from_nav'  # visaplan.plone.search v1.8.0+
    getExcludeFromSearch = 'getExcludeFromSearch'  # WIP: change index name
else:
    _vps_v = parse_version(_vps_v)
    if _vps_v < parse_version('1.8.0.dev1'):
        raise ImportError('Found visaplan.plone.search %s; '
                 'we need 1.8+, if any!' % (_vps_v,))
    # visaplan:
    from visaplan.plone.search.idxnames import (
        getExcludeFromNav,
        getExcludeFromSearch,
        )
