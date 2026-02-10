"""Logging configuration for football-club."""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return the application logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("football_club")
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
