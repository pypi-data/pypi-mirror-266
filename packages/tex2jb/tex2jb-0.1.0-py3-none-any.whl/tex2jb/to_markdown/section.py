from typing import Optional
from TexSoup import TexNode

from ..context import Context


def section_to_markdown(
    section_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the section node to markdown.
    It is a level one heading.
    It is the start of a markdown file.

    Parameters
    ----------
    section_node : TexNode
        The section node.

    Returns
    -------
    str
        The markdown representation of the section. A level one heading.
    """

    # Get section title
    section_title = section_node.args[0].string

    # The content is a level one heading
    markdown_content = f"# {section_title}\n"

    return markdown_content
