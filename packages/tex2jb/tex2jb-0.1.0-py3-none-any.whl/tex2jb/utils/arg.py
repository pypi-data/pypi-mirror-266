from typing import Optional
from TexSoup import TexNode
from TexSoup.data import BraceGroup, BracketGroup


def get_mandatory_arg(tex_node: TexNode) -> Optional[str]:
    """Get the first mandatory arg from a TexNode.

    Parameters
    ----------
    tex_node : TexNode
        The TexNode to extract the arg from.

    Returns
    -------
    Optional[str]
        The arg string if it exists, otherwise None.
    """

    try:
        # Get the first group with curly braces
        group: BraceGroup = next(
            filter(lambda group: isinstance(group, BraceGroup), tex_node.args)
        )

        # Extract the arg string
        arg = str(group.string)

        return arg

    except:
        return None


def get_optional_arg(tex_node: TexNode) -> Optional[str]:
    """Get the first optional arg from a TexNode.

    Parameters
    ----------
    tex_node : TexNode
        The TexNode to extract the arg from.

    Returns
    -------
    Optional[str]
        The arg string if it exists, otherwise None.
    """

    try:
        # Get the first group with square brackets
        group: BraceGroup = next(
            filter(lambda group: isinstance(group, BracketGroup), tex_node.args)
        )

        # Extract the arg string
        arg = str(group.string)

        return arg

    except:
        return None


def remove_args(tex_node: TexNode) -> None:
    """Remove all args from a TexNode.

    Notes
    -----
        Instead of
        ```
        tex_node.args = []
        ```
        one must use
        ```
        tex_node.expr.args = []
        ```

    Parameters
    ----------
    tex_node : TexNode
        The TexNode to remove the args from.
    """

    # Remove all args
    tex_node.expr.args = []
