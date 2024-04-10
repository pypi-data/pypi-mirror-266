from typing import Optional
import re
import json


EXERCISE_MAGIC_COMMENT_PREFIX = "% <tex2jb: exercise>"

BEGIN_EXERCISE_RE = re.compile(r"\\begin{exercise}")
CHAPTER_RE = re.compile(r"\\chapter")


def add_exercise_magic_comments(tex_content: str) -> str:
    """Add exercise magic comments to the tex content.
    Each magic comment contains the exercise number,
    which will be used to produce markdown content.

    Notes
    -----
        I use this workaround because the Exercise is not supported by Sphinx Proof.

    Parameters
    ----------
    tex_content : str
        The original tex content.

    Returns
    -------
    str
        The tex content with exercise magic comments.
    """

    new_tex_contents: list[str] = []
    tex_content_position = 0

    chapter_number = 0
    chapter_number_of_last_exercise: Optional[int] = None
    exercise_number_in_chaper: Optional[int] = None
    for mat in BEGIN_EXERCISE_RE.finditer(tex_content):

        # Get the number of chapters from the last exercise to this one
        num_chapters = len(
            CHAPTER_RE.findall(
                tex_content,
                # Start at the beginning of the current pointer, and
                # stop at the beginning of the exercise
                pos=tex_content_position,
                endpos=mat.start(),
            )
        )

        # Update chapter number
        chapter_number += num_chapters

        # Reset exercise number if the chapter changes
        if chapter_number != chapter_number_of_last_exercise:
            exercise_number_in_chaper = 1

        # Otherwise, increment the exercise number in the current chapter
        else:
            exercise_number_in_chaper += 1

        # Update the last chapter number
        chapter_number_of_last_exercise = chapter_number

        # Exercise number
        exercise_number = f"{chapter_number}.{exercise_number_in_chaper}"

        # Add tex content to buffer
        new_tex_contents.append(tex_content[tex_content_position : mat.end()])

        # Update tex content position
        tex_content_position = mat.end()

        # Encode the exercise number into JSON string
        json_str = json.dumps({"exercise_number": exercise_number})

        # Create magic comment
        magic_comment = f"{EXERCISE_MAGIC_COMMENT_PREFIX} {json_str}\n"

        # Add the magic comment to the new tex contents
        new_tex_contents.append(magic_comment)

    # Add the rest of tex content to buffer
    new_tex_contents.append(tex_content[tex_content_position:])

    # The new tex content
    new_tex_content = "".join(new_tex_contents)

    return new_tex_content


def is_exercise_magic_comment(magic_comment: str) -> bool:
    """Check if the magic comment is an exercise magic comment.

    Parameters
    ----------
    magic_comment : str
        The magic comment.

    Returns
    -------
    bool
        Whether the magic comment is an exercise magic comment.
    """

    return magic_comment.startswith(EXERCISE_MAGIC_COMMENT_PREFIX)


def extract_exercise_number(exercise_magic_comment: str) -> str:
    """Extract the exercise number from the exercise magic comment.

    Parameters
    ----------
    magic_comment : str
        The magic comment of the exercise.

    Returns
    -------
    str
        The exercise number, e.g., `"1.1"`, `"1.2"`.
    """

    # Get the JSON string
    json_string = exercise_magic_comment.removeprefix(
        EXERCISE_MAGIC_COMMENT_PREFIX
    ).strip()

    # Parse the JSON string
    exercise_number_dict: dict[str, str] = json.loads(json_string)

    # Get the exercise number
    exercise_number = exercise_number_dict["exercise_number"]

    return exercise_number
