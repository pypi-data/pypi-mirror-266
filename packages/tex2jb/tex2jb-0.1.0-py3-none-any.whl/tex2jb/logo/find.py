from typing import Optional
from pathlib import Path

from ..logging import logger
from .default_logo_svg import DEFAULT_LOGO_SVG
from .default_favicon_svg import DEFAULT_FAVICON_SVG


LOGO_EXTENSION_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
)

FAVICON_EXTENSION_SUFFIXES = (
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
)

DEFAULT_LOGO_FILE_NAME = "logo.svg"
DEFAULT_FAVICON_FILE_NAME = "favicon.svg"


def find_logo_and_favicon(book_dir: Path) -> tuple[Path, Path]:
    """Find logo and favicon in the book directory.
    If the logo or favicon is not found, create a default one.

    Parameters
    ----------
    book_dir : Path
        The root directory of the Jupyter Book.

    Returns
    -------
    tuple[Path, Path]
        The path to the logo and the path to the favicon.
    """

    # Find logo
    logo_path: Optional[Path] = None
    for suffix in LOGO_EXTENSION_SUFFIXES:
        try:
            logo_path = next(iter(book_dir.glob(f"*{suffix}")))
            break
        except:
            continue

    # Find favicon
    favicon_path: Optional[Path] = None
    for suffix in FAVICON_EXTENSION_SUFFIXES:
        try:
            favicon_path = next(iter(book_dir.glob(f"*{suffix}")))
            break
        except:
            continue

    # No logo is found
    # Create a default logo
    if logo_path is None:

        # Log
        logger.warning("No logo is found")

        # Set default logo path
        logo_path = book_dir.joinpath(DEFAULT_LOGO_FILE_NAME).absolute()

        # Create default logo
        with open(logo_path, "w") as f:
            f.write(DEFAULT_LOGO_SVG)

        # Log
        logger.info(f"Created a default logo at {logo_path}")

    # No favicon is found
    # Create a default favicon
    if favicon_path is None:

        # Log
        logger.warning("No favicon is found")

        # Set default favicon path
        favicon_path = book_dir.joinpath(DEFAULT_FAVICON_FILE_NAME).absolute()

        # Create default favicon
        with open(favicon_path, "w") as f:
            f.write(DEFAULT_FAVICON_SVG)

        # Log
        logger.info(f"Created a default favicon at {favicon_path}")

    return logo_path, favicon_path
