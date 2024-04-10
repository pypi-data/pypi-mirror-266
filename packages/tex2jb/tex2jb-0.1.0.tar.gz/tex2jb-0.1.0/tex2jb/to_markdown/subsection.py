from typing import Optional
from TexSoup import TexNode

from ..context import Context


def subsection_to_markdown(
    subsection_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the subsection node to markdown.
    It is a level two heading.

    Parameters
    ----------
    subsection_node : TexNode
        The subsection node.

    Returns
    -------
    str
        The markdown representation of the subsection. A level two heading.
    """

    # Get subsection title
    subsection_title = subsection_node.args[0].string

    # The content is a level two heading
    markdown_content = f"## {subsection_title}\n"

    return markdown_content
