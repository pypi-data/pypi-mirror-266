"""Clementine is a sweet little Python package."""
import logging

from clementine.about import __version__  # noqa: F401

logging.getLogger(__name__).addHandler(logging.NullHandler())
