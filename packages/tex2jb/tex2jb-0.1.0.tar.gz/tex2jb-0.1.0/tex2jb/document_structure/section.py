from typing import Any
from pydantic import BaseModel, model_serializer
from pathlib import Path


class Section(BaseModel):

    # `title` is not included in _toc.yml
    title: str

    # In the format of _toc.yml, file path is serialized as `file`
    file_path: Path

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:

        return {
            "file": str(self.file_path),
        }
