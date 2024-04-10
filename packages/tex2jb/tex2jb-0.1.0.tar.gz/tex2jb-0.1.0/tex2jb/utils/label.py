from typing import Optional
from TexSoup import TexNode


def get_label_marker(label_node: TexNode) -> str:
    """Get the label marker from the label node.

    Parameters
    ----------
    label_node : TexNode
        The label node.

    Returns
    -------
    str
        The label marker.
    """

    # Get the tex group
    group = label_node.args[0]

    # Note the type of this is `TexSoup.data.TexTex`, which is not a string
    label_marker = group.string

    # Convert to str
    label_marker = str(label_marker)

    return label_marker


def find_label_marker_in_tex_node(tex_node: TexNode) -> Optional[str]:
    """Find the label marker in contents of a tex node.

    Parameters
    ----------
    tex_node : TexNode
        The tex node.

    Returns
    -------
    Optional[str]
        The label marker.
    """

    # Find the label node
    label_node = tex_node.find("label")

    # No label is found
    if label_node is None:
        return None

    # Get the label marker
    label_marker = get_label_marker(label_node)

    return label_marker
