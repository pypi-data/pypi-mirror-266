from typing import Optional
from TexSoup import TexNode

from ..context import Context


def label_to_markdown(
    label_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the label node to markdown.
    Note that we do not handle the label's content here.
    Instead, the label content should be handled in each environment.

    Parameters
    ----------
    label_node : TexNode
        The label node.

    Returns
    -------
    str
        The markdown representation of the label. An empty string.
    """

    return ""
