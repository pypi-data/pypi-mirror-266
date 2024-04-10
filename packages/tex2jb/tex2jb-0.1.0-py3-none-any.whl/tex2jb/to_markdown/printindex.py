from typing import Optional
from TexSoup import TexNode

from ..context import Context

INDEX_TITLE = "Index"


def printindex_to_markdown(
    printindex_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the printindex node to markdown.
    It should be a level 1 heading.
    And the title is "Index" regardless of the custom titles.

    Reference
    ---------
        https://jupyterbook.org/en/stable/content/content-blocks.html#add-the-general-index-to-your-table-of-contents

    Parameters
    ----------
    printindex_node : TexNode
        The printindex node.

    Returns
    -------
    str
        The markdown representation of the printindex command.
    """

    return f"# {INDEX_TITLE}\n"
