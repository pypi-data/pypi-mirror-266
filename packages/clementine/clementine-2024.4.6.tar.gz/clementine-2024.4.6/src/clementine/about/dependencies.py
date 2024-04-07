"""Package dependencies for clementine."""

from dataclasses import dataclass
from typing import Union

__all__ = [
    "Extra",
    "dependencies",
    "extras",
    "optional_dependencies",
    "python_version",
    "recommended_dependencies",
]

_VERSIONS = {
    "bandit": "bandit[toml]",
    "black": "black",
    "bokeh": "bokeh",
    "build": "build",
    "catppuccin-matplotlib": "catppuccin-matplotlib",
    "click": "click",
    "datasets": "datasets",
    "gradio": "gradio",
    "isort": "isort",
    "keras": "keras>=3",
    "mkdocs-click": "mkdocs-click",
    "mkdocs-walt": "mkdocs-walt",
    "mkdocstrings": "mkdocstrings[python]",
    "mypy": "mypy",
    "numpy": "numpy",
    "notebook": "notebook",
    "pandas": "pandas",
    "pip-tools": "pip-tools",
    "playwright": "playwright",
    "pre-commit": "pre-commit",
    "pyperclip": "pyperclip",
    "pytest": "pytest",
    "rich": "rich",
    "ruff": "ruff",
    "scikit-learn": "scikit-learn",
    "spacy": "spacy",
    "tomlkit": "tomlkit",
    "torch": "torch>=2",
    "transformers": "transformers",
    "twine": "twine",
    "wandb": "wandb",
}


@dataclass(frozen=True)
class Extra:
    """Basic information about an extra dependency."""

    name: str
    description: str
    deps: tuple[str, ...]


_blossom = Extra(
    name="blossom",
    description="visualization and demonstration tools",
    deps=("bokeh", "gradio", "playwright"),
)

_fruit = Extra(
    name="fruit",
    description="machine learning libraries",
    deps=("catppuccin-matplotlib", "keras", "numpy", "pandas", "scikit-learn", "torch"),
)

_leaves = Extra(
    name="leaves",
    description="documentation tools",
    deps=("mkdocs-click", "mkdocs-walt", "mkdocstrings"),
)

_pulp = Extra(
    name="pulp",
    description="auxiliary ml libraries",
    deps=("datasets", "spacy", "transformers", "wandb"),
)

_rind = Extra(
    name="rind",
    description="packaging tools",
    deps=("build", "tomlkit", "twine"),
)

_seeds = Extra(
    name="seeds",
    description="general development tools",
    deps=(
        "bandit",
        "black",
        "isort",
        "mypy",
        "pip-tools",
        "pre-commit",
        "pytest",
        "ruff",
    ),
)

_sprout = Extra(
    name="sprout",
    description="exploration and prototyping tools",
    deps=("notebook", "rich"),
)

_tree = Extra(
    name="tree",
    description="all optional dependencies",
    deps=(
        *_blossom.deps,
        *_fruit.deps,
        *_leaves.deps,
        *_pulp.deps,
        *_rind.deps,
        *_seeds.deps,
        *_sprout.deps,
    ),
)


def _make_deps_list(package_names: Union[list[str], tuple[str, ...]]) -> list[str]:
    """Returns a list of dependencies with their constraints.

    Args:
      package_names: The names of the packages to include.

    Raises:
      ValueError: If a `package_name` is not a known dependencies.
    """
    deps = []
    for package_name in package_names:
        if package_name not in _VERSIONS:
            raise ValueError(
                f"Package '{package_name}' is not a known dependencies: "
                f"{list(_VERSIONS.keys())}"
            )
        deps.append(_VERSIONS[package_name])
    return deps


def dependencies() -> list[str]:
    """Returns a list of clementine's required dependencies."""
    return []


def optional_dependencies() -> dict[str, list]:
    """Returns a dictionary of clementine's optional dependencies."""
    return {
        "all": _make_deps_list(["click", "playwright", "pyperclip"]),
    }


def extras() -> tuple[Extra, ...]:
    """Returns a tuple of clementine's recommended dependencies as `Extra`s."""
    return (_blossom, _fruit, _leaves, _pulp, _rind, _seeds, _sprout, _tree)


def recommended_dependencies() -> dict[str, list]:
    """Returns a dictionary of recommended dependencies.

    The recommended dependencies are a collection of libraries and frameworks
    you might want to use when starting a new project. These dependencies aren't
    necessarily used in clementine, but they're made available as extra packages
    for easier installation."""
    return {extra.name: _make_deps_list(extra.deps) for extra in extras()}


def python_version() -> str:
    """Returns clementine's required Python version."""
    return ">=3.9"
