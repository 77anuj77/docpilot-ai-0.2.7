"""ParseDoc Logging utilities"""

import logging
import sys


def setup_logging(verbose: bool = False, quiet: bool = False):
    """Configure and return the parsedoc logger.

    Args:
        verbose: Enable DEBUG level logging.
        quiet: Suppress INFO/DEBUG, only WARNING and above.

    Returns:
        A configured logging.Logger instance.
    """
    level = logging.DEBUG if verbose else logging.INFO
    if quiet:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    return logging.getLogger("parsedoc")


def get_logger(name: str = "parsedoc") -> logging.Logger:
    """Return a logger scoped under parsedoc."""
    return logging.getLogger(name)
