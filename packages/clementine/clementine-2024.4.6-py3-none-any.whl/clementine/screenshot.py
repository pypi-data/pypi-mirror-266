"""Screenshot utilities."""

import asyncio
import os
from typing import Any, Optional

from clementine import env, importing

__all__ = ["async_screenshot", "screenshot"]

_PLAYWRIGHT_IMPORT_ERROR_MESSAGE = (
    "The Playwright Python package is not installed. Install it with "
    "`pip install playwright`. Install Playwright's browser dependencies with "
    "`playwright install webkit`."
)

pw_async_api = importing.maybe_import_module(
    "playwright.async_api", _PLAYWRIGHT_IMPORT_ERROR_MESSAGE
)
pw_api_types = importing.maybe_import_module(
    "playwright._impl._api_types", _PLAYWRIGHT_IMPORT_ERROR_MESSAGE
)


async def async_screenshot(
    url: str,
    *,
    output_dir: Optional[str] = None,
    filename: Optional[str] = None,
    full_page: bool = False,
    **kwargs: Optional[dict[str, Any]],
) -> list[str]:
    """Asynchronously take screenshots of a webpage in light and dark mode."""
    output_dir = output_dir or os.path.join(os.getcwd(), "screenshots")
    filename = filename or "screenshot"
    color_schemes = ("light", "dark")
    output_paths = []

    async with pw_async_api.async_playwright() as p:
        try:
            browser = await p.webkit.launch()
        except pw_api_types.Error as e:
            raise OSError(
                "The browser could not be launched. Install the Playwright "
                "browser dependencies with `playwright install webkit`."
            ) from e

        page = await browser.new_page()
        await page.goto(url)

        os.makedirs(output_dir, exist_ok=True)
        for color_scheme in color_schemes:
            await page.emulate_media(color_scheme=color_scheme)
            path = os.path.join(output_dir, f"{filename}-{color_scheme}.png")
            await page.screenshot(path=path, full_page=full_page, **kwargs)
            output_paths.append(path)

        await browser.close()

    return output_paths


def screenshot(
    url: str,
    *,
    output_dir: Optional[str] = None,
    filename: Optional[str] = None,
    full_page: bool = False,
    **kwargs: Optional[dict[str, Any]],
) -> list[str]:
    """Take screenshots of a webpage in light and dark mode.

    Use `screenshot.async_screenshot()` in asynchronous contexts, such as in a
    Jupyter notebook. Use `screenshot.screenshot()` in synchronous contexts,
    such as in a synchronous Python script.

    Prerequisites:

    1. Install the Playwright Python package: `pip install playwright`.
    2. Install the Playwright browser dependencies: `playwright install webkit`.

    Example usage in a Python script:

    ```python
    from clementine import screenshot

    paths = screenshot.screenshot('https://example.com')
    ```

    Example usage in a Jupyter notebook or other asynchronous context:

    ```python
    from clementine import screenshot
    from IPython.display import display, Image

    paths = await screenshot.async_screenshot('https://example.com')
    for path in paths:
        display(Image(path, width=600))
    ```

    Args:
      url: The URL to take screenshots of. The URL must include the scheme, e.g.
        https:// or file:///.
      output_dir: The directory to save the screenshots to. Defaults to
        'screenshots' in the current working directory.
      filename: The base filename to use for the screenshots. Defaults to
        'screenshot'. The screenshots will be saved as screenshot-light.png and
        screenshot-dark.png, for example.
      full_page: Whether to take a screenshot of the full page. Defaults to False.
      **kwargs: Extra arguments to `playwright.async_api.Page.screenshot`. See
        playwright's documentation for all possible arguments:
        <https://playwright.dev/docs/api/class-page#page-screenshot>

    Raises:
      ImportError: If the Playwright Python package is not installed.
      Error: If the browser cannot be launched or an invalid url is provided.
      RuntimeError: If called in an asynchronous context.

    Returns:
      A list of the paths to the screenshots.
    """
    if env.is_notebook():
        raise RuntimeError(
            "The function `screenshot.screenshot()` cannot be called in "
            "an asynchronous context, such as in a Jupyter notebook. "
            "Use `screenshot.async_screenshot()` instead."
        )
    return asyncio.run(
        async_screenshot(
            url, output_dir=output_dir, filename=filename, full_page=full_page, **kwargs
        )
    )
