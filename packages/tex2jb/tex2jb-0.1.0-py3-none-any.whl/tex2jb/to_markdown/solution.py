from typing import Optional
from TexSoup import TexNode

from ..context import Context
from .tex_environment import tex_environment_body_to_markdown


def solution_to_markdown(
    solution_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Begin the solution block
    # * It is a custom admonition
    begin_solution_block_str = f"\n````{{admonition}} Solution\n"
    markdown_contents.append(begin_solution_block_str)

    # Admonition class attribute
    # * Add dropdown class to hide the solution body
    markdown_contents.append(f":class: solution dropdown\n")

    # Markdown of the solution body
    markdown_contents.extend(
        tex_environment_body_to_markdown(solution_node, context=context)
    )

    # End the solution block
    end_solution_block_str = "\n````\n"
    markdown_contents.append(end_solution_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
