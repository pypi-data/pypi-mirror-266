from typing import Optional
from TexSoup import TexNode

from ..context import Context
from .tex_environment import tex_environment_body_to_markdown


def proof_to_markdown(
    proof_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Begin the proof block
    begin_proof_block_str = "\n````{prf:proof}\n"
    markdown_contents.append(begin_proof_block_str)

    # Markdown of the proof body
    body_content = tex_environment_body_to_markdown(proof_node, context=context)

    # * If the body is empty,
    # * then set it to double newlines to avoid an empty block
    # * Otherwise Jupyter Book will throw an error
    if body_content.strip() == "":
        body_content = "\n\n"

    markdown_contents.extend(body_content)

    # End the proof block
    end_proof_block_str = "\n````\n"
    markdown_contents.append(end_proof_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
