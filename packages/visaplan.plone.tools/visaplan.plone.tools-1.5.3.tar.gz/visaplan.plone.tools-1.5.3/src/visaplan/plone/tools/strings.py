# Python compatibility:
from __future__ import absolute_import

import six

is_encoded = isinstance(s, str)  # Python 2: str
is_unicode = isinstance(s, six.text_type)  # Python 2: unicode
is_anystring = isinstance(s, six.string_types)  # Python 2: basestring
is_bytes = isinstance(s, bytes)
