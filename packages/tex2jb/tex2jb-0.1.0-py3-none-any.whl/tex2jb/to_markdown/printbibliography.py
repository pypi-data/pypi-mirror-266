from typing import Optional
from TexSoup import TexNode

from ..context import Context

DEFAULT_BIBLIOGRAPHY_TITLE = "Bibliography"


def printbibliography_to_markdown(
    printbibliography_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the printbibliography node to markdown.
    It should be a level 1 heading followed by a bibliography directive.

    Parameters
    ----------
    printbibliography_node : TexNode
        The printbibliography node.

    Returns
    -------
    str
        The markdown representation of the printbibliography command.
    """

    markdown_contents: list[str] = []

    args = printbibliography_node.args
    if len(args) == 0:
        title = DEFAULT_BIBLIOGRAPHY_TITLE
    else:

        # Get thw optional argument
        printbibliography_optional_arg_str: str = str(args[0].string)

        # Extract the options
        printbibliography_options = {}
        for item_str in printbibliography_optional_arg_str.split(","):

            # Remove leading and trailing spaces
            item_str = item_str.strip()

            # Extract the key and value
            key, value = item_str.split("=")

            printbibliography_options[key] = value

        # Get the custom title
        if "title" in printbibliography_options:
            title = printbibliography_options["title"]

        else:
            title = DEFAULT_BIBLIOGRAPHY_TITLE

    # Level 1 heading
    markdown_contents.append(f"# {title}\n")

    # Bibliography directive
    markdown_contents.append("\n```{bibliography}\n```\n")

    markdown_content = "".join(markdown_contents)

    return markdown_content
