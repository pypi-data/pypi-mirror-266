from typing import Optional
from TexSoup import TexNode

from ..context import Context


def part_to_markdown(
    part_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the part node to markdown.
    It is an empty string.

    Parameters
    ----------
    part_node : TexNode
        The part node.

    Returns
    -------
    str
        The markdown representation of the part. An empty string.
    """

    return ""
