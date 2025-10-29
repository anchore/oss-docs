#!/usr/bin/env python3
"""
Centralized logging configuration for documentation generation scripts.

Provides consistent, pretty logging across all scripts using the rich library.
"""

import logging

from rich.console import Console
from rich.logging import RichHandler


def setup(verbosity: int = 0, script_name: str | None = None) -> logging.Logger:
    """
    configure logging with RichHandler for pretty output.

    Args:
        verbosity: verbosity level (0=WARNING, 1=INFO, 2=DEBUG)
        script_name: optional script name for logger (defaults to root logger)

    Returns:
        configured logger instance

    Examples:
        >>> # in a script with click
        >>> @click.option("-v", "--verbose", count=True)
        >>> def main(verbose: int):
        ...     logger = log.setup(verbose, __file__)
        ...     logger.info("Starting script...")
    """
    # map verbosity count to log level
    level_map = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    log_level = level_map.get(verbosity, logging.DEBUG)

    # create rich console for stdout output to be able to easily grep
    console = Console(stderr=False)

    # configure rich handler with clean formatting
    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=verbosity >= 2,  # show locals only in debug mode
        show_time=False,  # disable timestamp for cleaner output
        show_path=verbosity >= 2,  # show file path only in debug mode
        markup=True,  # enable rich markup in log messages
    )

    # configure logging format
    # in INFO mode: just the message
    # in DEBUG mode: level name + message
    if verbosity >= 2:
        log_format = "%(message)s"
    else:
        log_format = "%(message)s"

    rich_handler.setFormatter(logging.Formatter(log_format))

    # get or create logger
    if script_name:
        # extract script name from path (e.g., "/path/to/script.py" -> "script")
        import os

        script_basename = os.path.basename(script_name)
        logger_name = script_basename.replace(".py", "")
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    # clear any existing handlers
    logger.handlers.clear()

    # add rich handler
    logger.addHandler(rich_handler)
    logger.setLevel(log_level)

    # suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    return logger


def logger(name: str | None = None) -> logging.Logger:
    """
    get a logger instance for use in utility modules.

    this function assumes setup() has already been called
    by the main script entrypoint.

    Args:
        name: logger name (e.g., __name__)

    Returns:
        logger instance that inherits from root logger configuration

    Examples:
        >>> # in a utility module
        >>> logger = log.logger(__name__)
        >>> logger.debug("Processing data...")
    """
    return logging.getLogger(name)
