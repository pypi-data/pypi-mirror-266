from typing import Optional
from pydantic import BaseModel
from pathlib import Path


class Context(BaseModel):

    # The path to the tex file to convert
    tex_path: Optional[Path] = None

    # The root directory of the Jupyter Book contents to generate
    book_dir: Path = None

    markdown_file_path: Optional[Path] = None
    exercise_label_marker_to_number: Optional[dict[str, str]] = None
