from pydantic import BaseModel

from .part import Part


class TableOfContents(BaseModel):

    format: str = "jb-book"
    root: str = "intro"
    parts: list[Part]
