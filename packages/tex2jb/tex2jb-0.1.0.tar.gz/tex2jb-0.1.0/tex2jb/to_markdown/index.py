from typing import Optional
from TexSoup import TexNode

from ..context import Context


def index_to_markdown(
    index_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the index node to markdown.
    Note that we do not handle the index's content here.
    Instead, the index content should be handled using magic comments.

    Parameters
    ----------
    index_node : TexNode
        The index node.

    Returns
    -------
    str
        The markdown representation of the index. An empty string.
    """

    return ""
