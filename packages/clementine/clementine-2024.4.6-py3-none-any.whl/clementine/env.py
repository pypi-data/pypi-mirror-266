"""Environment utilities."""

import builtins
import importlib.metadata
import importlib.util
import platform
from typing import Optional

__all__ = ["ensure_is_available", "info", "is_available", "is_notebook"]


def is_available(package: str) -> bool:
    """Returns True if a package is installed or is a built-in.

    Args:
      package: The name of the package to verify.
    """
    return importlib.util.find_spec(package) is not None


def ensure_is_available(package: str, message: Optional[str] = None):
    """Raises a ModuleNotFoundError if a package is not importable.

    Args:
      package: The name of the package to verify.
      message: The error message to display.
    """
    if not is_available(package):
        message = message or f"No module named '{package}'"
        raise ModuleNotFoundError(message)


# Inspired by https://github.com/explosion/spaCy/blob/master/spacy/cli/info.py
def info(packages: Optional[list[str]] = None) -> dict[str, str]:
    """Returns package installation and environment information.

    Args:
      packages: The names of the packages whose metadata should be included.
    """
    env = {
        "Python version": platform.python_version(),
        "Platform": platform.platform(),
    }

    if packages:
        for package in packages:
            try:
                env[f"{package} version"] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                env[f"{package} version"] = "Not installed."

    return env


def is_notebook() -> bool:
    """Returns True if the current environment is a Jupyter notebook."""
    return getattr(builtins, "__IPYTHON__", False)
