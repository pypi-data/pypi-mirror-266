# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1
"""
collective.metadataversion: exceptions

The exceptions defined here are intended to be raised by code of the
collective.metadataversion package *only*; the calling signature might change.
However, the hierarchy of classes can be relied on:

ReindexingBaseException
|- UsageError
|  |- UsageTypeError
|  `- UsageValueError
`- ReindexingError
   `- ObjectNotFound
"""

class ReindexingBaseException(Exception):
    """\
    Base exception for this package
    """
    def __init__(self, message, cause=None):
        self.message = message
        self.cause = cause

    def __str__(self):
        return self.message


# ----------------------------------------------- [ usage errors ... [
class UsageError(ReindexingBaseException):
    "An error occured before actually trying to reindex anything"


class UsageTypeError(UsageError, TypeError):
    "A wrong option was specified"


class UsageValueError(UsageError, ValueError):
    "A wrong value was specified"
# ----------------------------------------------- ] ... usage errors ]


# ------------------------------------------- [ operation errors ... [
class ReindexingError(ReindexingBaseException):
    "There was a problem reindexing an object."


class ObjectNotFound(ReindexingError):
    "Could not get the indexed object"
# ------------------------------------------- ] ... operation errors ]
