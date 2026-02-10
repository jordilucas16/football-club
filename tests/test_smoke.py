"""Smoke tests to verify basic functionality."""

import pytest

from football_club import __version__
from football_club.config import Config
from football_club.logging import setup_logging


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_config_defaults():
    """Test that config has sensible defaults."""
    config = Config()
    assert config.environment == "development"
    assert config.log_level == "INFO"
    assert config.debug is False


def test_logging_setup():
    """Test that logging can be configured."""
    logger = setup_logging("DEBUG")
    assert logger.name == "football_club"
    assert logger.level == 10  # DEBUG level
