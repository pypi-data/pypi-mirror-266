# -*- encoding: utf-8 -*-
import logging

import logzero
from logzero import logger as _logger

DEFAULT_FORMAT = "%(color)s[%(levelname)1.4s]%(end_color)s %(message)s"
# Set a custom formatter
formatter = logzero.LogFormatter(fmt=DEFAULT_FORMAT)


def setup(verbose):
    logzero.setup_default_logger(formatter=formatter)
    level = logging.DEBUG if verbose else logging.INFO

    _logger.setLevel(level)
    _logger.debug("Logging as %s", level)


def debug(message, *args, **kwargs):
    _logger.debug(message, *args, **kwargs)


def info(message, *args, **kwargs):
    _logger.info(message, *args, **kwargs)


def warning(message, *args, **kwargs):
    _logger.warning(message, *args, **kwargs)


def error(message, *args, **kwargs):
    _logger.error(message, *args, **kwargs)
