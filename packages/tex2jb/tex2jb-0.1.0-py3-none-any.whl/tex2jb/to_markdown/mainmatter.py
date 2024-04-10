from typing import Optional
from TexSoup import TexNode

from ..context import Context


def mainmatter_to_markdown(
    mainmatter_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the mainmatter node to markdown.
    It is an empty string.

    Parameters
    ----------
    mainmatter_node : TexNode
        The mainmatter node.

    Returns
    -------
    str
        The markdown representation of the `\\mainmatter`. An empty string.
    """

    return ""
