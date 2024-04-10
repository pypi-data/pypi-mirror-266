from pathlib import Path

INTRO_FILE_NAME = "intro.md"

INTRO_MARKDOWN_CONTENT_TEMPLATE = """
# Introduction

Welcome to {book_title}.

## Table of Contents

```{{tableofcontents}}
```
"""


def create_intro_markdown(book_dir: Path, book_title: str) -> Path:
    """Create a default intro markdown file.

    Parameters
    ----------
    book_dir : Path
        The root directory of the Jupyter Book.

    book_title : str
        The title of the Jupyter Book.

    Returns
    -------
    Path
        The path to the created intro markdown file.
    """

    # Complete the intro markdown content
    intro_markdown_content = INTRO_MARKDOWN_CONTENT_TEMPLATE.format(
        book_title=book_title,
    )

    # Write to file
    with open(book_dir.joinpath(INTRO_FILE_NAME), "w") as f:
        f.write(intro_markdown_content)

    return book_dir.joinpath(INTRO_FILE_NAME)
