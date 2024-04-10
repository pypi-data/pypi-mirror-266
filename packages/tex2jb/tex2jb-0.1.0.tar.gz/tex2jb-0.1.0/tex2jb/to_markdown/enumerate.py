from typing import Optional
from TexSoup import TexNode

from ..context import Context
from .tex_element import tex_elements_to_markdown


def enumerate_to_markdown(
    enumerate_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Find all items
    item_nodes = enumerate_node.find_all("item")

    # Markdown of each item
    for index, item_node in enumerate(item_nodes):
        item_index = index + 1
        item_content = tex_elements_to_markdown(item_node.contents)
        item_content = f"{item_index}. {item_content}"
        markdown_contents.append(item_content)

    markdown_content = "".join(markdown_contents)

    return markdown_content
