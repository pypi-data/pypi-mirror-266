from typing import Optional
from TexSoup import TexNode

from ..context import Context


def tableofcontents_to_markdown(
    tableofcontents_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the tableofcontents node to markdown.
    It is an empty string.

    Parameters
    ----------
    tableofcontents_node : TexNode
        The tableofcontents node.

    Returns
    -------
    str
        The markdown representation of the `\\tableofcontents`. An empty string.
    """

    return ""
