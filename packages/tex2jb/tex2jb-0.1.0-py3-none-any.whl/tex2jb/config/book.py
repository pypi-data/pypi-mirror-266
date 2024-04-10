from pydantic import BaseModel

from .execution import ExecutionSettings
from .parse import ParseSettings
from .html import HTMLSettings
from .latex import LatexSettings
from .launch_buttons import LaunchButtonsSettings
from .repository import RepositorySettings
from .sphinx import SphinxSettings


class BookSettings(BaseModel):
    """
    Reference
    ---------
        https://jupyterbook.org/en/stable/customize/config.html#configuration-defaults
    """

    title: str
    author: str

    # List of bibtex files
    bibtex_bibfiles: list[str] = []

    # Copyright year to be placed in the footer
    copyright: str = "2023"

    # A path to the book logo
    logo: str = ""

    # Patterns to skip when building the book. Can be glob-style (e.g. "*skip.ipynb")
    exclude_patterns: list[str] = [
        "_build",
        "Thumbs.db",
        ".DS_Store",
        "**.ipynb_checkpoints",
    ]

    # Auto-exclude files not in the toc
    only_build_toc_files: bool = False

    # Execution settings
    execute: ExecutionSettings = ExecutionSettings()

    # Parse settings
    parse: ParseSettings = ParseSettings()

    # HTML settings
    html: HTMLSettings = HTMLSettings()

    # LaTeX settings
    latex: LatexSettings = LatexSettings()

    # Launch buttons settings
    launch_buttons: LaunchButtonsSettings = LaunchButtonsSettings()

    # Repository settings
    repository: RepositorySettings = RepositorySettings()

    # Sphinx settings
    sphinx: SphinxSettings = SphinxSettings()
