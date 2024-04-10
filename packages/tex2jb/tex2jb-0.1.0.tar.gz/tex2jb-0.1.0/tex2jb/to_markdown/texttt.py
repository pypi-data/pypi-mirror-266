from typing import Optional
from TexSoup import TexNode

from ..context import Context


def texttt_to_markdown(
    texttt_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the texttt node to markdown.

    Parameters
    ----------
    texttt_node : TexNode
        The texttt node.

    Returns
    -------
    str
        The markdown representation of the texttt.
    """

    # Get the text content
    text_content: str = texttt_node.args[0].string

    # Add addtional whitespace around ` ` delimiters to avoid potential conflicts
    return f" `{text_content}` "
