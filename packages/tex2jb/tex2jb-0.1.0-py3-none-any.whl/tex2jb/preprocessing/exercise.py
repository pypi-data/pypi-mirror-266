from TexSoup import TexNode

from ..utils import find_label_marker_in_tex_node
from ..tex_element_type import TexElementType, get_tex_element_type
from ..magic_comments import is_exercise_magic_comment, extract_exercise_number


def construct_exercise_label_marker_to_number(root_node: TexNode) -> dict[str, str]:
    """Construct a dictionary that maps exercise label marker to exercise number.

    Parameters
    ----------
    root_node : TexNode
        The root node of the LaTeX file.

    Returns
    -------
    dict[str, str]
        A dictionary that maps exercise label marker to exercise number.
    """

    # A dictionary that maps exercise label marker to exercise number
    exercise_label_marker_to_number: dict[str, str] = {}

    exercise_node: TexNode
    for exercise_node in root_node.find_all("exercise"):

        # Find the label marker
        label_marker = find_label_marker_in_tex_node(exercise_node)
        if label_marker is None:
            continue

        # Find the exercise magic comment
        # It must be the first comment in the exercise environment
        for element in exercise_node.contents:

            # Get element type
            element_type = get_tex_element_type(element)

            # Get the exercise magic comment
            if element_type == TexElementType.COMMENT:
                exercise_magic_comment = element
                break

        assert is_exercise_magic_comment(
            exercise_magic_comment
        ), "The exercise magic comment is not found"

        # Extract the exercise number
        exercise_number = extract_exercise_number(exercise_magic_comment)

        # Set the key-value pair
        exercise_label_marker_to_number[label_marker] = exercise_number

    return exercise_label_marker_to_number
