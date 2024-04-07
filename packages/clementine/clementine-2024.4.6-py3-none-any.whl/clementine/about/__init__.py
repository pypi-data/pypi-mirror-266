"""Some metadata for the clementine package."""

import webbrowser

__title__ = "clementine"
__description__ = "🍊 clementine is a sweet little Python package."
__author__ = "Suzen Fylke"
__version__ = "2024.4.6"  # Calver with format YYYY.MM.DD
__pretty_version__ = f"{__title__} v{__version__}"
__documentation__ = "https://codesue.github.io/clementine"
__repository__ = "https://github.com/codesue/clementine"


def docs():
    """Opens the documentation website in a browser."""
    webbrowser.open(__documentation__)


def repo():
    """Opens the repository website in a browser."""
    webbrowser.open(__repository__)
