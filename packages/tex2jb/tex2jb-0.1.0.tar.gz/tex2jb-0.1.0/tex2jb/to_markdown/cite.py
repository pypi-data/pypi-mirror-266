from typing import Optional
from TexSoup import TexNode

from ..context import Context


def cite_to_markdown(
    cite_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the cite node to markdown.

    Parameters
    ----------
    cite_node : TexNode
        The cite node.

    Returns
    -------
    str
        The markdown representation of the cite command.
    """

    # Get bibtex key
    bibtex_key: str = str(cite_node.args[0].string)

    # Markdown content
    return f"{{cite}}`{bibtex_key}`"
