from pathlib import Path

from .custom_admonition_css import (
    CUSTOM_ADMONITION_CSS_FILE_NAME,
    CUSTOM_ADMONITION_CSS,
)
from ..logging import logger


STATIC_DIR_NAME = "_static"


def create_static_dir(book_dir: Path) -> Path:

    # Get the static dir
    static_dir = book_dir.joinpath(STATIC_DIR_NAME)
    static_dir.mkdir(parents=True, exist_ok=True)

    # Log
    logger.info(f"Created static dir at {static_dir}")

    # Write custom admonition CSS
    with open(static_dir.joinpath(CUSTOM_ADMONITION_CSS_FILE_NAME), "w") as f:
        f.write(CUSTOM_ADMONITION_CSS)

        # Log
        logger.info(
            f"Created custom admonition CSS at {static_dir.joinpath(CUSTOM_ADMONITION_CSS_FILE_NAME)}"
        )
