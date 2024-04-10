# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1

# We might make this adjustable one day, if the need arises.
# Note that this would make it necessary to create our metadata column by
# code rather than simply by catalog.xml
VERSION_KEY = 'metadata_version'
FULL_VERSION_KEY = 'collective.metadataversion.interfaces.IMetadataSettings.metadata_version'

# Which indexes to we refresh for "metadata-only" reindexing?
FULL_IDXS_KEY = 'collective.metadataversion.interfaces.IMetadataSettings.default_idxs'
DEFAULT_IDXS = ['getId']
