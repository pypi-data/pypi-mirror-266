from pydantic import BaseModel

from .tex_macros import Mathjax3Config


class SphinxConfig(BaseModel):

    bibtex_reference_style: str = "author_year"

    mathjax3_config: Mathjax3Config = Mathjax3Config()
