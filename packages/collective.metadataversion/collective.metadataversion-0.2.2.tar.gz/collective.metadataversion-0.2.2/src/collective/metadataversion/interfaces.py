# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1
"""
collective.metadataversion: interfaces
"""

# Python compatibility:
from __future__ import absolute_import

# Zope:
from zope import schema

# Plone:
from plone.supermodel import model

# Local imports:
from ._i18n import _
from .config import DEFAULT_IDXS


class IMetadataSettings(model.Schema):
    metadata_version = schema.Int(
        title=_(u'Metadata version'),
        default=0,
        description=_(
            u'help_metadata_version',
            default=u'This value is set to the metadata_version attribute '
            u'of every brain whenever an object is reindexed with '
            u'update_metadata=True; this helps you to reindex objects only '
            u'when needed, and reindex more later, skipping the already '
            u'reindexed objects.'))

    default_idxs = schema.List(
        title=_(u'Default indexes'),
        value_type=schema.BytesLine(title=_(u'ID of an index')),
        default=DEFAULT_IDXS,
        missing_value=DEFAULT_IDXS,
        description=_(
            u'help_default_idxs',
            default=u'Specify a (short) list of very "cheap" indexes '
            u'to be refreshed when metadata-only reindexing is requested, '
            u'e.g. [getId].\n'
            u'NOTE: '
            u'This affects only operations which use this value explicitly, '
            u'like the use of an updater which was created by '
            u'collective.metadataversion.utils.make_metadata_updater.'))
