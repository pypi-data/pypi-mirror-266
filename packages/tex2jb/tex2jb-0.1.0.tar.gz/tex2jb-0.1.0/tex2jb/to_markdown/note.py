from typing import Optional
from TexSoup import TexNode

from ..context import Context
from .tex_environment import tex_environment_body_to_markdown


def note_to_markdown(
    note_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Begin the note block
    # * I use ::: here to avoid conficts of nested admonitions
    begin_note_block_str = "\n:::{note}\n"
    markdown_contents.append(begin_note_block_str)

    # Markdown of the note body
    markdown_contents.extend(
        tex_environment_body_to_markdown(note_node, context=context)
    )

    # End the note block
    end_note_block_str = "\n:::\n"
    markdown_contents.append(end_note_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
