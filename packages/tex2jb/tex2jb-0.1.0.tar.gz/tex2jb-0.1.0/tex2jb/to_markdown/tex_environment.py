from typing import Optional
from TexSoup import TexNode

from ..context import Context
from ..utils import remove_args
from .tex_element import tex_element_to_markdown


def tex_environment_body_to_markdown(
    environment_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # * Remove the args of the environment so that they are not included in the markdown
    remove_args(environment_node)

    for tex_element in environment_node.contents:
        # Markdown of the tex element
        content = tex_element_to_markdown(tex_element, context=context)

        # Collect the content
        markdown_contents.append(content)

    markdown_content = "".join(markdown_contents)

    return markdown_content
