from pathlib import Path
import shutil
from typing import Optional
from TexSoup import TexNode
from TexSoup.data import BraceGroup

from ..context import Context
from ..utils import find_label_marker_in_tex_node
from ..logging import logger


def figure_to_markdown(
    figure_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # Find the \includegraphics command
    includegraphics_node: TexNode = figure_node.find("includegraphics")

    # The figure path arg is contained in a BraceGroup
    figure_path_arg = next(
        filter(lambda group: isinstance(group, BraceGroup), includegraphics_node.args)
    )

    # Get the tex figure path
    assert context.tex_path is not None, "Tex path is not set"
    tex_parent_dir = context.tex_path.parent
    tex_figure_path = tex_parent_dir.joinpath(figure_path_arg.string).absolute()

    # Get the figure file name
    figure_name = tex_figure_path.name

    # Get the figure path in the Jupyter Book
    assert context.book_dir is not None, "Book directory is not set"
    book_figures_dir = context.book_dir.joinpath(tex_figure_path.parent.name)
    book_figures_dir.mkdir(parents=True, exist_ok=True)
    book_figure_path = book_figures_dir.joinpath(figure_name).absolute()

    # Copy the figure to the Jupyter Book directory
    shutil.copy(tex_figure_path, book_figure_path)

    # Log
    logger.info(f"Copied {tex_figure_path} to {book_figure_path}")

    # To make Jupyter Book know where to find the figure
    # in a figure directive,
    # we need to use abosolute path,
    # and the root path "/" is the book directory
    # For example, "/figures/my-figure.jpg"
    directive_figure_path = Path("/").joinpath(
        book_figure_path.relative_to(context.book_dir.absolute())
    )

    # Find the \caption command
    caption_node: TexNode = figure_node.find("caption")

    # Extract the caption
    figure_caption = str(caption_node.string)

    # Begin the figure directive
    markdown_contents.append(f"```{{figure}} {directive_figure_path}\n")

    # Begin metadata
    markdown_contents.append("---\n")

    # Find the label marker if there is one
    label_marker = find_label_marker_in_tex_node(figure_node)

    if label_marker is not None:

        # The name proerty is the label of the figure
        markdown_contents.append(f"name: {label_marker}\n")

    # End metadata
    markdown_contents.append("---\n")

    # Caption
    markdown_contents.append(f"{figure_caption}\n")

    # End the figure directive
    markdown_contents.append("```\n")

    markdown_content = "".join(markdown_contents)

    return markdown_content
