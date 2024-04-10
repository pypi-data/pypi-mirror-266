from typing import Optional
from TexSoup import TexNode

from ..utils import find_label_marker_in_tex_node, get_optional_arg
from .tex_environment import tex_environment_body_to_markdown
from ..context import Context


def definition_to_markdown(
    definition_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Get the title if there is one
    title = get_optional_arg(definition_node)
    title = "" if title is None else str(title)

    # Begin the definition block
    begin_definition_block_str = f"\n````{{prf:definition}} {title}\n"
    markdown_contents.append(begin_definition_block_str)

    # Find the label marker if there is one
    label_marker = find_label_marker_in_tex_node(definition_node)

    if label_marker is not None:

        # Set the label
        markdown_contents.append(f":label: {label_marker}\n")

    # Markdown of the definition body
    markdown_contents.extend(
        tex_environment_body_to_markdown(definition_node, context=context)
    )

    # End the definition block
    end_definition_block_str = "\n````\n"
    markdown_contents.append(end_definition_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
