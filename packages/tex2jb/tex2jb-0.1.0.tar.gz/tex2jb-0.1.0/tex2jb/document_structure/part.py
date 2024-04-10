from typing import Optional
from pydantic import BaseModel

from .chapter import Chapter


class Part(BaseModel):

    caption: Optional[str] = None
    numbered: bool
    chapters: list[Chapter]
