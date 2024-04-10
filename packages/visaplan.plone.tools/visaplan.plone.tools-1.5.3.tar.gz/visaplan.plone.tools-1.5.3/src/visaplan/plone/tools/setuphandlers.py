# -*- coding: utf-8 -*-
"""
There is currently absolutely no point in "activation" of this package as an add-on;
since we did so before, we try to support clean deactivation.

So, please DON'T activate!
We try our best not to trigger you to do so.
"""
# Python compatibility:
from __future__ import absolute_import

__author__ = """Tobias Herp <tobias.herp@visaplan.com>"""
__docformat__ = 'plaintext'

# Zope:
from zope.interface import implementer

# Plone:
from Products.CMFPlone.interfaces import INonInstallable

# ------------------------------------------------------ [ Daten ... [
PROJECTNAME = u'visaplan.plone.tools'
PROFILE_ID = PROJECTNAME + u':default'
LOGGER_LABEL = PROJECTNAME + u': setuphandlers'
# ------------------------------------------------------ ] ... Daten ]


@implementer(INonInstallable)
class Hidden(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            PROJECTNAME + u':uninstall',
        ]

    def getNonInstallableProducts(self):
        """
        There is *nothing* in this package which could be "installed"!
        """
        return [PROJECTNAME]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.

