from typing import Optional
from TexSoup import TexNode

from ..context import Context


def text_to_markdown(
    text_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the text node to markdown.
    It should be exactly the LaTeX expression of itself, e.g, `\\text{hello}`.

    Parameters
    ----------
    text_node : TexNode
        The text node.

    Returns
    -------
    str
        The markdown representation of the text,
        which is exactly the LaTeX expression of itself.
    """

    return str(text_node)
