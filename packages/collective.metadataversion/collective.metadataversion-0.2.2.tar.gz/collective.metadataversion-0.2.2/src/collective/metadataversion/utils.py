# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1
"""
collective.metadataversion: utilities

We don't provide browser views to get and set our metadata_version;
we don't need to, since we use the standard Plone registry.

However, we like some comfort using our unintrusive little metadata column,
and for this reason we provide a little utility here;
see the ../../../README.rst file for a short usage description.
"""

# Python compatibility:
from __future__ import absolute_import

__all__ = [
    'make_metadata_updater',
    'extract_mmu_kwargs',  # helper for functions to call the former
    ]

try:
    # Zope:
    from Missing import Value as Missing_Value
    from Products.CMFCore.utils import getToolByName
    from ZODB.POSException import ConflictError
    from zope.component import getUtility

    # Plone:
    from plone.registry.interfaces import IRegistry

    # Local imports:
    from .config import FULL_IDXS_KEY, FULL_VERSION_KEY, VERSION_KEY
    from .exceptions import (
        ObjectNotFound,
        ReindexingError,
        UsageTypeError,
        UsageValueError,
        )
except ImportError as e:
    if __name__ == '__main__':  # doctest
        VERSION_KEY = 'metadata_version'
        FULL_VERSION_KEY = ('collective.metadataversion.interfaces'
                            '.IMetadataSettings.metadata_version')
        FULL_IDXS_KEY = ('collective.metadataversion.interfaces'
                         '.IMetadataSettings.default_idxs')
        IRegistry = None  # good enough for our doctest
        fake_registry = {
            FULL_VERSION_KEY: 42,
            FULL_IDXS_KEY: ['getId'],
            }
        def getUtility(*args, **kw):
            return fake_registry
        HAVE_MISSING = 0
        Missing_Value = ''
        class ReindexingError(Exception):
            def __init__(self, message, cause=None):
                self.message = message
                self.cause = cause
            def __str__(self):
                return self.message
        class ObjectNotFound(ReindexingError): pass
        UsageTypeError = TypeError
        UsageValueError = ValueError
        ConflictError = Exception
    else:
        raise
else:
    HAVE_MISSING = 1


def _update_mmu_kwargs(context, logger, metadata_version, kwargs):
    """
    Update a kwargs dict, injecting 'new_version' and 'minimum_version' keys.

    NOTE: This function is for internal use, and both the signature and
          the functionality may change without notice!

    For our test, the registry will be a simple dict object containing our key:

    >>> FULL_VERSION_KEY = 'metadata_version'
    >>> def getUtility(*args, **kw):
    ...     return {FULL_VERSION_KEY: 42}

    The context argument is needed only to get the portal_catalog,
    so None is sufficient for this function:

    >>> def ummu(metadata_version, kwargs):
    ...     _update_mmu_kwargs(None, None, metadata_version, kwargs)
    ...     return sorted(kwargs.items())

    We can specify a smaller than the recorded version, which will be used for
    comparisons as intended; but it won't be stored by default:
    >>> kw = {}
    >>> ummu(41, kw)                          # doctest: +NORMALIZE_WHITESPACE
    [('change',        None),
     ('idxs',         ['getId']),
     ('minimum_version', 41),
     ('new_version',   None),
     ('old_version',     42)]

    ... unless we force it to be accepted:
    >>> kw = dict(force_version=1)
    >>> ummu(41, kw)                          # doctest: +NORMALIZE_WHITESPACE
    [('change',        None),
     ('idxs',         ['getId']),
     ('minimum_version', 41),
     ('new_version',     41),
     ('old_version',     42)]

    This has updated our registry value; thus, a call without a new version
    will result in:
    >>> kw = {}
    >>> ummu(None, kw)                        # doctest: +NORMALIZE_WHITESPACE
    [('change',        None),
     ('idxs',         ['getId']),
     ('minimum_version', 41),
     ('new_version',   None),
     ('old_version',     41)]

    While we don't necessarily handle *all* legal options here,
    we still reject unknown options, raising the usual TypeError:

    >>> ummu(None, dict(minimum_version=40))
    Traceback (most recent call last):
      ...
    TypeError: Illegal argument(s): minimum_version

    """
    force_version = kwargs.pop('force_version', False)
    strict = kwargs.pop('strict', True)
    if metadata_version is not None:
        if not isinstance(metadata_version, int):
            raise UsageValueError('integer number expected;'
                                  ' found %(metadata_version)r'
                                  % locals())
        if metadata_version < 0:
            raise UsageValueError('integer number >=0 expected;'
                                  ' found %(metadata_version)r'
                                  % locals())
    elif force_version:
        raise UsageValueError('With force_version given, '
                              'we expect a non-None metadata_version!')
    unused = set(kwargs) - set(['idxs', 'force_indexes',
                                'update_metadata',
                                'change',  # a function(object, logger)
                                'debug',
                                ])
    if unused:
        unused = sorted(unused)
        if strict:
            raise UsageTypeError('Illegal argument(s): %s'
                                 % ', '.join(unused))
        else:
            for key in unused:
                val = kwargs.pop(key)
                logger.warn('IGNORING unknown option %(key)s=%(val)r', locals())

    registry = getUtility(IRegistry)
    old_version = registry.get(FULL_VERSION_KEY)
    new_version = None
    if metadata_version > old_version:
        registry[FULL_VERSION_KEY] = minimum_version = new_version = metadata_version
    elif force_version:
        assert isinstance(metadata_version, int)  # see above: not None
        registry[FULL_VERSION_KEY] = minimum_version = new_version = metadata_version
    elif metadata_version is None:
        minimum_version = old_version or 0
    else:
        assert metadata_version <= old_version
        assert isinstance(metadata_version, int)
        minimum_version = metadata_version

    if 'idxs' not in kwargs:
        if kwargs.get('force_indexes'):
            idxs = None  # refresh all indexes
        else:
            idxs = list(registry[FULL_IDXS_KEY])  # default: a cheap subset
        kwargs['idxs'] = idxs

    kwargs.setdefault('change', None)  # a function(object, logger)
    kwargs.update({
        # metadata_version value, stored in the registry:
        'new_version':     new_version,  # if not None, written to registry
        'old_version':     old_version,  # ... from registry
        # the metadata_version (always a number >= 0)
        # the brain objects are compared to:
        'minimum_version': minimum_version,
        })


def make_metadata_updater(context, logger=None, metadata_version=None,
                          **kwargs):
    """
    Persistently update the metadata_version and return an updater function.

    Arguments:

    context -- the context (usually the portal)
    logger -- a logger, used to tell e.g. about the set and/or active
              metadata_version; if not given, we'll create one.
    metadata_version -- an integer number, or None.
                   If a number, it should be greater than the previously active
                   version; otherwise, the number won't be stored unless
                   affirmed by force_version=True (below).

    The further arguments are "keyword-only":

    force_version -- change the target metadata_version even if smaller than
                   the previously active version. We expect this to be used
                   for development only.

    idxs -- (forwarded to catalog.reindexObject)
            The indexes to be updated in case an object's metadata is to be
            updated.  The default value depends on the value of the
            force_indexes option:

            - If falsy (default), we use a "cheap selection"
              (like configured; e.g. ['getId']),
              simply to make the metadata refresh happen;
            - otherwise, the default is `None`, causing all indexes to be
              updated (but -- with update_metadata=None (the default) -- not
              necessarily the metadata as well).

            Note that we *do* care if idxs=None is explicitly specified --
            this will be honoured, and no "cheap subset" is used! --
            or not.
    force_indexes -- Refresh the indexes (according to the idxs option above)
            even if the metadata is already up-to-date.

    Thus, if you *specify* ``idxs=None`` but not `force_indexes`, all indexes
    will be updated as well if the metadata is considered outdated.

    change -- a function(object, logger) to be called before reindexing is
              performed.
              As what we do depends on the metadata_version found in the
              catalog object, this function call does so as well:
              If our negotiation concludes to not reindex, this function won't
              be called, either.
              Currently the returned value is ignored;
              if the changes applied by the function might cause more idxs to
              rot, you currently need to add those to the list (for all),
              or to specify idxs=None (which will include all indexes).

    ... and finally:

    update_metadata -- Refresh the metadata columns?

        We are not sure yet whether the non-default values make any sense.
        However, the possible values are:

            None (the default) -- refresh brains without a current
                                  metadata_version
            True -- refresh even up-to-date brains
            False -- suppress metadata updates.  *Note* that this will cause
                     the metadata_version column not to be updated either!
    """
    if logger is None:
        logger = logging.getLogger('reindex')
    _update_mmu_kwargs(context, logger, metadata_version, kwargs)
    assert 'new_version' in kwargs
    catalog = getToolByName(context, 'portal_catalog')
    catalog_reindex = catalog.reindexObject

    idxs = kwargs['idxs']
    new_version = kwargs['new_version']
    old_version = kwargs['old_version']
    minimum_version = kwargs['minimum_version']
    was = (new_version > old_version) and 'was' or 'is'
    logger.info('metadata_version %(was)s %(old_version)r', locals())
    if new_version is None:
        if metadata_version is not None and minimum_version < old_version:
            logger.warn('metadata_version NOT changed to %(minimum_version)d'
                        ' because smaller than %(old_version)d'
                        ' (perhaps try force_version=True?)', locals())
    else:
        logger.info('metadata_version changed to %(new_version)d', locals())
    logger.info('metadata_version will be set to %d'
                ' for all reindexed objects',
                old_version if new_version is None
                else new_version)
    logger.info('metadata_version will be compared to %(minimum_version)d',
                locals())

    force_indexes = kwargs.get('force_indexes', False)
    update_metadata = kwargs.get('update_metadata', None)
    _info = ['comparing metadata_version to %(minimum_version)d' % locals(),
             idxs and 'indexes: ' + ', '.join(idxs) or 'all indexes',
             ]
    debug = kwargs.pop('debug', False)
    if debug:
        _info.append('DEBUG')

    logger.info('make_metadata_updater: ' + '; '.join(_info))
    change = kwargs['change']
    if change is None:
        pass
    elif not callable(change):
        raise ValueError("change option is expected to be a function"
                '(object, logger); found %s' % (type(change),))
    else:
        logger.info('The %(change)r function(object, logger) will be '
                    'called before reindexing an object', locals())

    def reindex(brain):
        """
        Reindex the object given as brain.
        """
        # if this fails, there is a general problem;
        # e.g., you need to run catalog.xml first
        current_version = brain.metadata_version
        REINDEXED, ERROR = False, None

        # '' > 0 > None; we distinguish between 0 and None
        if HAVE_MISSING:
            if current_version is Missing_Value:
                current_version = None
        else:
            if current_version == Missing_Value:
                current_version = None

        if update_metadata is None:  # the default
            refresh_metadata = current_version < minimum_version
        elif update_metadata:
            refresh_metadata = 1
        else:
            refresh_metadata = 0

        if not refresh_metadata and not force_indexes:
            return False

        try:
            o = brain.getObject()
        except Exception as e:
            logger.exception(e)
            txt = '%(brain)r.getObject() FAILED!' % locals()
            logger.error(txt)
            raise ObjectNotFound(txt, e)
        else:
            if o is None:
                txt = '%(brain)r.getObject() returned None!' % locals()
                logger.error(txt)
                raise ObjectNotFound(txt, e)

        try:
            if change is not None:
                res = change(o, logger)
                if res is not None:
                    logger.debug('%(res)r <-- change(%(o)r, ...)', locals())
                    # we might e.g. inject indexes to be updated ...
                    logger.warn('change(%(o)r: Currently, the returned value '
                                'is ignored!', locals())
            catalog_reindex(o, idxs=idxs, update_metadata=refresh_metadata)
        except IOError as e:
            # There is a likely source for IOError exception:
            # PIL (or Pillow), objecting to an unsupported image format.
            # Of course such errors should be caught by the respective indexer,
            # allowing for the rest of the objects to be reindexed;
            # but for now, we like to avoid the whole job to fail
            # just because of very few foul objects.
            msg = e.message
            fail = 1
            cause = ''
            if msg is not None:
                if (msg == 'unrecognized data stream contents'
                           ' when reading image file'
                    or msg.startswith('cannot find loader for this ')
                    ):
                    cause = ' (PIL)'
                    fail = 0
            logger.error('IOError reindexing %(o)r%(cause)s: %(e)r', locals())
            if fail:
                raise ReindexingError('Error reindexing %(o)r' % locals(),
                                      e)
            else:
                return False
        except ConflictError as e:
            logger.error('ConflictError reindexing %(o)r: %(e)r', locals())
            # ConflictErrors must never be masked, right?
            raise
        except KeyboardInterrupt:
            logger.error('INTERRUPTED reindexing %(o)r!', locals())
            raise
        except Exception as e:
            logger.error('error reindexing %(o)r: %(e)r', locals())
            raise ReindexingError('Error reindexing %(o)r' % locals(),
                                  e)
        else:
            return True

    return reindex


def extract_mmu_kwargs(kw, do_pop=1):
    """
    Little helper for functions which call make_metadata_updater

    With do_pop=1 (the default), the known keys are removed from the source
    keywords dict:

    >>> kw = {'the_answer': 42, 'force_version': 1}
    >>> extract_mmu_kwargs(kw)
    {'force_version': 1}
    >>> kw
    {'the_answer': 42}

    To keep the source dict unchanged, you can specify do_pop=0.
    The following example contains all currently extracted keys:

    >>> kw = {
    ... 'the_answer': 42,
    ... 'metadata_version': 24,
    ... 'idxs': ['getId', 'sortable_title'],
    ... 'force_version': 0,
    ... 'force_indexes': 1,
    ... }
    >>> sorted(extract_mmu_kwargs(kw, 0).items())
    ...                               # doctest: +NORMALIZE_WHITESPACE
    [('force_indexes',    1),
     ('force_version',    0),
     ('idxs',             ['getId', 'sortable_title']),
     ('metadata_version', 24)]
    >>> sorted(kw.items())            # doctest: +NORMALIZE_WHITESPACE
    [('force_indexes',    1),
     ('force_version',    0),
     ('idxs',             ['getId', 'sortable_title']),
     ('metadata_version', 24),
     ('the_answer',       42)]
    """
    res = {}
    get = (kw.pop if do_pop else kw.get)
    for key in (
        'metadata_version',
        'idxs',
        'force_version', 'force_indexes',
        'change',  # function(object, logger)
        ):
        if key in kw:
            res[key] = get(key)
    return res


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
