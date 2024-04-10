# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1
"""
collective.metadataversion: "indexers" (more precisely, metadata adapters)
"""
# Python compatibility:
from __future__ import absolute_import

# Zope:
from Products.CMFCore.interfaces import IContentish
from zope.component import getUtility

# Plone:
from plone.indexer import indexer
from plone.registry.interfaces import IRegistry

# Local imports:
from .config import FULL_VERSION_KEY


@indexer(IContentish)
def metadata_version(object):
    # simply return the current value, as last set
    registry = getUtility(IRegistry)
    return registry[FULL_VERSION_KEY]
