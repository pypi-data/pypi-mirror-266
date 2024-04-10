from TexSoup import TexNode, TexSoup

from .tilde_suffix import remomve_words_with_tilde_suffix
from ..magic_comments import add_index_magic_comments, add_exercise_magic_comments
from .exercise import construct_exercise_label_marker_to_number
from ..context import Context
from ..logging import logger


def preprocess_tex(tex_content: str) -> tuple[TexNode, Context]:

    # Remove words with tilde(~) suffixes
    tex_content = remomve_words_with_tilde_suffix(tex_content)

    # Add magic comments
    tex_content = add_index_magic_comments(tex_content)
    tex_content = add_exercise_magic_comments(tex_content)

    # Parse the tex content
    logger.info("Parsing tex content...")
    root_node = TexSoup(tex_content)
    logger.info("Done parsing tex content")

    # Construct the exercise label marker to number
    exercise_label_marker_to_number = construct_exercise_label_marker_to_number(
        root_node
    )

    # Set context
    context = Context(
        exercise_label_marker_to_number=exercise_label_marker_to_number,
    )

    return root_node, context
