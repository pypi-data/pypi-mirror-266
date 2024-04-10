# -*- coding: utf-8 -*- vim: sw=4 sts=4 si et ts=8 tw=79 cc=+1
"""
Decorator for upgrade steps
"""

# Python compatibility:
from __future__ import absolute_import

# Standard library:
from functools import wraps
from time import time

# Logging / Debugging:
import logging

__all__ = [
        # decorators:
        'step',
        # exceptions:
        'StepAborted',
        ]


class StepAborted(Exception):
    """
    Vom Dekorator @step geworfen, wenn in einem Migrationsschritt eine
    KeyBoard-Exception ausgelöst wurde
    """


def step(func):
    """
    Dekorator für Migrationsschritte:
    - ergänzt ggf. fehlendes logger-Argument
    - stoppt die Zeit
    - (experimentell:)
      erlaubt das Weiterlaufen der Zope-Instanz auch nach manuellem Abbruch
      des Migrationsschritts
    """
    # da die def-Anweisung hier nicht ausgeführt wird, ist eine implizite
    # "Impfung" der verpackten Funktion mit zusätzlichen Variablen (wie z.B.
    # "site") leider nicht möglich; dafür würden zusätzliche Argumente
    # benötigt, und mithin eine Änderung der Signatur.

    @wraps(func)
    def wrapper(context, logger=None):
        funcname = func.__name__
        if logger is None:
            logger = logging.getLogger('setup:'+funcname)
        _started = time()
        try:
            res = func(context, logger)
        except Exception as e:
            delta = time() - _started
            if isinstance(e, KeyboardInterrupt):
                logger.error('%(funcname)s aborted after %(delta)5.2f seconds',
                             locals())
                logger.exception(e)
                raise StepAborted
            else:
                logger.error('%(funcname)s: %(e)r after %(delta)5.2f seconds',
                             locals())
                logger.exception(e)
                raise
        else:
            delta = time() - _started
            logger.info('%(res)r <-- %(funcname)s (%(delta)5.2f seconds)', locals())
        return res

    return wrapper
