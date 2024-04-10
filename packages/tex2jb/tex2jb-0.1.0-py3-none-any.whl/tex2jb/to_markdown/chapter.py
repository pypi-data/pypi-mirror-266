from typing import Optional
from TexSoup import TexNode

from ..context import Context


def chapter_to_markdown(
    chapter_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the chapter node to markdown.
    It is a level one heading.
    It is the start of the special index.md file,
    which is the index file for all sections in the chapter.

    Parameters
    ----------
    chapter_node : TexNode
        The chapter node.

    Returns
    -------
    str
        The markdown representation of the chapter. A level one heading.
    """

    # Get chapter title
    chapter_title = chapter_node.args[0].string

    # The content is a level one heading
    markdown_content = f"# {chapter_title}\n"

    return markdown_content
