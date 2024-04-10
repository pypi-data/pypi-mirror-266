from typing import Optional
from TexSoup import TexNode

from ..context import Context
from ..utils import find_label_marker_in_tex_node
from .tex_environment import tex_environment_body_to_markdown


def align_to_markdown(
    align_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Begin the math block
    begin_math_block_str = "\n```{math}\n"
    markdown_contents.append(begin_math_block_str)

    # Find the label marker if there is one
    label_marker = find_label_marker_in_tex_node(align_node)

    if label_marker is not None:

        # Set the label
        markdown_contents.append(f":label: {label_marker}\n")

    # Markdown of the environment body
    markdown_contents.extend(
        tex_environment_body_to_markdown(align_node, context=context)
    )

    # End the math block
    end_math_block_str = "\n```\n"
    markdown_contents.append(end_math_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
