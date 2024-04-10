from typing import Optional
from TexSoup import TexNode

from ..context import Context


def frontmatter_to_markdown(
    frontmatter_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the frontmatter node to markdown.
    It is an empty string.

    Parameters
    ----------
    frontmatter_node : TexNode
        The frontmatter node.

    Returns
    -------
    str
        The markdown representation of the `\\frontmatter`. An empty string.
    """

    return ""
