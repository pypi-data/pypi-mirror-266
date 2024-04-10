from typing import Optional
from TexSoup import TexNode

from ..context import Context


def eqref_to_markdown(
    eqref_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the eqref node to markdown.
    The markdown content will be {eq}`<label marker>`.

    Parameters
    ----------
    eqref_node : TexNode
        The eqref node.

    Returns
    -------
    str
        The markdown representation of the eqref command.
    """

    # Get label marker
    label_marker: str = eqref_node.args[0].string

    return f"{{eq}}`{label_marker}`"
