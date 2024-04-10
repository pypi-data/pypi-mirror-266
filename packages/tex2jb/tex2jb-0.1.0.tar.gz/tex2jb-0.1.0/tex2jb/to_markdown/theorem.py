from typing import Optional
from TexSoup import TexNode

from ..context import Context
from ..utils import find_label_marker_in_tex_node, get_optional_arg
from .tex_environment import tex_environment_body_to_markdown


def theorem_to_markdown(
    theorem_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Get the title if there is one
    title = get_optional_arg(theorem_node)
    title = "" if title is None else str(title)

    # Begin the theorem block
    begin_theorem_block_str = f"\n````{{prf:theorem}} {title}\n"
    markdown_contents.append(begin_theorem_block_str)

    # Find the label marker if there is one
    label_marker = find_label_marker_in_tex_node(theorem_node)

    if label_marker is not None:

        # Set the label
        markdown_contents.append(f":label: {label_marker}\n")

    # Markdown of the theorem body
    markdown_contents.extend(
        tex_environment_body_to_markdown(theorem_node, context=context)
    )

    # End the theorem block
    end_theorem_block_str = "\n````\n"
    markdown_contents.append(end_theorem_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
