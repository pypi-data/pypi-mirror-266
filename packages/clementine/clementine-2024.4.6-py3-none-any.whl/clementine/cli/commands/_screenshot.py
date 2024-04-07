"""The clementine CLI screenshot commands."""

from clementine import importing
from clementine.screenshot import screenshot as _screenshot

click = importing.maybe_import_module("click")


@click.command()
@click.argument("url")
@click.option(
    "-o",
    "--output-dir",
    help=(
        'The directory to save the screenshots to. Defaults to "screenshots" '
        "in the current working directory."
    ),
)
@click.option(
    "-f",
    "--filename",
    help=(
        'The base filename to use for the screenshots. Defaults to "screenshot". '
        "The screenshots will be saved as screenshot-light.png and "
        "screenshot-dark.png, for example."
    ),
)
@click.option(
    "--full-page/--no-full-page",
    default=False,
    help="Whether to take a screenshot of the full page. Defaults to False.",
)
def screenshot(url, output_dir, filename, full_page):
    """Take screenshots of a webpage in light and dark mode. The URL must include
    the scheme, e.g. https:// or file:///.
    """
    paths = _screenshot(
        url, output_dir=output_dir, filename=filename, full_page=full_page
    )
    click.echo(f"The screenshots of {url} were saved at these paths: ")
    for path in paths:
        click.echo(f"- {path}")
