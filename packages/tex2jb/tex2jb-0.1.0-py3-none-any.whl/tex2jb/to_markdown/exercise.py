from typing import Optional
from TexSoup import TexNode
from TexSoup.data import Token

from ..context import Context
from ..utils import find_label_marker_in_tex_node
from .tex_environment import tex_environment_body_to_markdown
from ..tex_element_type import TexElementType, get_tex_element_type
from ..magic_comments import is_exercise_magic_comment, extract_exercise_number


def exercise_to_markdown(
    exercise_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:

    markdown_contents: list[str] = []

    # * The label in the markdown is before the exercise block

    # Find the label marker if there is one
    label_marker = find_label_marker_in_tex_node(exercise_node)

    if label_marker is not None:

        # Set the label
        # Reference: https://jupyterbook.org/en/stable/start/new-file.html#create-your-file-and-add-content-to-it
        markdown_contents.append(f"({label_marker})=")

    # Find the exercise magic comment
    # It must be the first comment in the exercise environment
    exercise_magic_comment: Optional[Token] = None
    for tex_element in exercise_node.contents:

        # Get element type
        element_type = get_tex_element_type(tex_element)

        # Get the exercise magic comment
        if element_type == TexElementType.COMMENT:
            exercise_magic_comment = tex_element
            assert is_exercise_magic_comment(
                exercise_magic_comment
            ), "The first comment in the exercise is not a magic comment"
            break

    assert exercise_magic_comment is not None, "The exercise magic comment is not found"

    # Get the exercise number from the magic comment
    exercise_number = extract_exercise_number(exercise_magic_comment)

    # Begin the exercise block
    # * It is a custom admonition
    # * The title of the admonition is like `Exercise <exercise_number>`
    begin_exercise_block_str = f"\n````{{admonition}} Exercise {exercise_number}\n"
    markdown_contents.append(begin_exercise_block_str)

    # Admonition class attribute
    markdown_contents.append(f":class: exercise\n")

    # Markdown of the exercise body
    markdown_contents.extend(
        tex_environment_body_to_markdown(exercise_node, context=context)
    )

    # End the exercise block
    end_exercise_block_str = "\n````\n"
    markdown_contents.append(end_exercise_block_str)

    markdown_content = "".join(markdown_contents)

    return markdown_content
