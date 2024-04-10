from typing import Optional
from TexSoup import TexNode

from ..context import Context


def textbf_to_markdown(
    textbf_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the textbf node to markdown.

    Parameters
    ----------
    textbf_node : TexNode
        The textbf node.

    Returns
    -------
    str
        The markdown representation of the textbf.
    """

    # Get the text content
    text_content: str = textbf_node.args[0].string

    # Add addtional whitespace around ** ** delimiters to avoid potential conflicts
    return f" **{text_content}** "
