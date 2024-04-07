"""The clementine CLI."""

from clementine import about, importing
from clementine.cli import commands

click = importing.maybe_import_module("click")

_CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}


@click.group(context_settings=_CONTEXT_SETTINGS, help=about.__description__)
@click.version_option(
    about.__version__, "-v", "--version", message=about.__pretty_version__
)
def main():
    """The main entry point for the clementine CLI."""
    pass


main.add_command(commands.info)
main.add_command(commands.screenshot)

if __name__ == "__main__":
    main()
