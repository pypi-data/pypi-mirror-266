from typing import Optional
from TexSoup import TexNode

from ..utils import find_label_marker_in_tex_node
from .tex_environment import tex_environment_body_to_markdown
from ..context import Context


def example_to_markdown(
    example_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Begin the example block
    begin_example_block_str = "\n````{prf:example}\n"
    markdown_contents.append(begin_example_block_str)

    # Find the label marker if there is one
    label_marker = find_label_marker_in_tex_node(example_node)

    if label_marker is not None:

        # Set the label
        markdown_contents.append(f":label: {label_marker}\n")

    # Markdown of the example body
    markdown_contents.extend(
        tex_environment_body_to_markdown(example_node, context=context)
    )

    # End the example block
    end_example_block_str = "\n````\n"
    markdown_contents.append(end_example_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
