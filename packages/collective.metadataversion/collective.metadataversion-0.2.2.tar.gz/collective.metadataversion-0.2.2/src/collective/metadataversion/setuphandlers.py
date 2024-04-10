# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1
"""
setuphandler module for collective.metadataversion
"""
# Python compatibility:
from __future__ import absolute_import

__author__ = """Tobias Herp <tobias.herp@visaplan.com>"""
__docformat__ = 'plaintext'

# Zope:
from zope.interface import implementer

# Plone:
from plone.app.upgrade.utils import loadMigrationProfile
from Products.CMFPlone.interfaces import INonInstallable

# Local imports:
from .decorator import step

# Logging / Debugging:
import logging

LOGGER_LABEL = 'collective.metadataversion: setuphandlers'
logger = logging.getLogger(LOGGER_LABEL)

PROFILE_ID = 'collective.metadataversion:default'
CONTEXT_ID = 'profile-' + PROFILE_ID

def somebody_elses_problem(context):
    return context.readDataFile("collective.metadataversion-default.marker") is None


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if somebody_elses_problem(context): return

    site = context.getSite()
    # ... (not used yet)


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'collective.metadataversion:uninstall',
        ]

@step
def reload_gs_profile(context, logger):
    if somebody_elses_problem(context):
        return
    loadMigrationProfile(
        context,
        'profile-collective.metadataversion:default',
    	)
