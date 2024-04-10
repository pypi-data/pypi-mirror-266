from typing import Optional
from pydantic import BaseModel
from pathlib import Path
import yaml

from .book import BookSettings
from .html import HTMLSettings
from .repository import RepositorySettings
from .sphinx import SphinxSettings
from .sphinx.config import SphinxConfig, Mathjax3Config, Tex


class SimplifiedBookSettings(BaseModel):

    title: str
    author: str

    # List of bibtex files
    bibtex_bibfiles: list[str]

    # A path to the book logo
    logo: str

    # A path to a favicon image
    html_favicon: str

    # The URL to your book's repository
    repository_url: str

    # A list of extra extensions to load by Sphinx (added to those already used by JB)
    sphinx_extra_extensions: list[str] = []

    # A path to the tex macros file
    tex_macros_path: Optional[Path] = None

    @property
    def tex_macros(self) -> dict[str, str | list[str]]:
        """Custom tex macros."""

        if self.tex_macros_path is None:
            return {}

        with open(self.tex_macros_path, "r") as f:
            return yaml.safe_load(f)

    def to_book_settings(self) -> BookSettings:
        """Convert to a `BookSettings` instance.

        Returns
        -------
        BookSettings
            Congiguration for the Jupyter Book.
        """

        return BookSettings(
            title=self.title,
            author=self.author,
            bibtex_bibfiles=self.bibtex_bibfiles,
            logo=self.logo,
            html=HTMLSettings(
                favicon=self.html_favicon,
            ),
            repository=RepositorySettings(
                url=self.repository_url,
            ),
            sphinx=SphinxSettings(
                extra_extensions=self.sphinx_extra_extensions,
                config=SphinxConfig(
                    mathjax3_config=Mathjax3Config(
                        tex=Tex(
                            macros=self.tex_macros,
                        ),
                    ),
                ),
            ),
        )
