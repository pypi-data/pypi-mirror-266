"""Importing utilities."""

import importlib
from types import ModuleType
from typing import Optional, Union

__all__ = ["MissingModulePlaceholder", "maybe_import_module"]


# Inspired by https://github.com/koaning/embetter/blob/main/embetter/error.py
class MissingModulePlaceholder:
    """A placeholder for a module that is not installed. This allows us to
    defer raising an error until the module is actually used.
    """

    def __init__(self, name: str, message: Optional[str] = None):
        """Initializes a MissingModulePlaceholder.

        Example usage:

        ```python
        from clementine import importing

        try:
            import spacy
        except ImportError:
            spacy = importing.MissingModulePlaceholder("spacy")
        ```

        Args:
          name: The name of the package.
          message: An error message.
        """
        self._name = name
        self._message = message or (
            f"The package {name} is not installed. Install it with "
            f"`pip install {name}`."
        )

    def __getattr__(self, *args, **kwargs):
        """Raises a ModuleNotFoundError when an attribute is accessed."""
        raise ModuleNotFoundError(self._message)

    def __call__(self, *args, **kwargs):
        """Raises a ModuleNotFoundError when the object is called."""
        raise ModuleNotFoundError(self._message)


def maybe_import_module(
    name: str, message: Optional[str] = None
) -> Union[ModuleType, MissingModulePlaceholder]:
    """Tries to import a module by name and return it. If the module can't be
    imported, a placeholder object is returned instead.

    Example usage:

    ```python
    from clementine import importing

    spacy = importing.maybe_import_module("spacy")
    ```

    Args:
      name: The name of the module to import.
      message: An error message to pass to the placeholder object.
    """
    try:
        return importlib.import_module(name)
    except ImportError:
        return MissingModulePlaceholder(name, message)
