"""The clementine CLI info commands."""

from clementine import about, importing
from clementine.env import info as _info

click = importing.maybe_import_module("click")
pyperclip = importing.maybe_import_module("pyperclip")


@click.command()
@click.option(
    "--clipboard/--no-clipboard",
    default=False,
    help="Whether to copy the information to the clipboard. Defaults to False.",
)
def info(clipboard):
    """Show information about your environment and clementine installation."""
    env = "\n".join([f"{k}: {v}" for k, v in _info([about.__title__]).items()])
    if clipboard:
        pyperclip.copy(env)
    click.echo(env)
