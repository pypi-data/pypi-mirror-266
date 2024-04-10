Changelog
=========


0.2.2 (2023-02-14)
------------------

New Features:

- `change` option to .utils.make_metadata_updater
  (a function(object, logger), called before reindexing)

Improved exception handling:

- When catching IOErrors while reindexing, we inspect the message text;
  quite likely it's PIL (or Pillow) objecting to an unsupported image format.
  If so, we log the error, return False, and proceed to the next object.
  This usually implies the indexes and metadata refresh for the respective object to *fail,*
  but for the whole rest we should succeed.

  *Of course,* the error handling should better happen in the respective indexer!

- `ConflictError` and `KeyboardInterrupt` exceptions during reindexing are logged
  and re-raised.

[tobiasherp]


0.2.1 (2022-03-04)
------------------

New Features:

- New function .utils.extract_mmu_kwargs

Improvements:

- Improved the docstring of .utils.make_metadata_updater

[tobiasherp]


0.2.0 (2021-11-17)
------------------

Bugfixes:

- Register the ``metadata_version`` indexer,
  and
- attach it to IContentish

New Features:

- New setting ``default_idxs`` to adjust the (cheap!) indexes
  to be refreshed for "metadata-only" updates

[tobiasherp]


0.1.0 (2021-09-21)
------------------

- Initial release.
  [tobiasherp]
