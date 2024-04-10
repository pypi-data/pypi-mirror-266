from typing import Optional
from TexSoup import TexNode

from ..context import Context


def textit_to_markdown(
    textit_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the textit node to markdown.

    Parameters
    ----------
    textit_node : TexNode
        The textit node.

    Returns
    -------
    str
        The markdown representation of the textit.
    """

    # Get the text content
    text_content: str = textit_node.args[0].string

    # Add addtional whitespace around * * delimiters to avoid potential conflicts
    return f" *{text_content}* "
