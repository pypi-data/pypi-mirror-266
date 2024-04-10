from typing import Any
from pydantic import BaseModel, model_serializer
from pathlib import Path

from .section import Section


class Chapter(BaseModel):

    # `title` is not included in _toc.yml
    title: str

    # In the format of _toc.yml, file path is serialized as `file`
    file_path: Path

    sections: list[Section]

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:

        # Ignore empty sections
        if len(self.sections) == 0:
            return {
                "file": str(self.file_path),
            }

        return {
            "file": str(self.file_path),
            "sections": [section.model_dump() for section in self.sections],
        }
