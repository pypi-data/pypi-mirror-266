import re
import json


INDEX_MAGIC_COMMENT_PREFIX = "% <tex2jb: index>"

INDEX_RE = re.compile(r"\\index{[^\{\}]+}")
CHAPTER_RE = re.compile(r"\\chapter{[^\{\}]+}")
SECTION_RE = re.compile(r"\\section{[^\{\}]+}")
DOUBLE_NEWLINES_RE = re.compile(r"\n\n")


def add_index_magic_comments(tex_content: str) -> str:
    """Add index magic comments to the tex content.
    Each magic comment contains the index entry,
    which will be used to produce markdown content.

    Parameters
    ----------
    tex_content : str
        The original tex content.

    Returns
    -------
    str
        The tex content with index magic comments.
    """

    # New tex contents
    new_tex_contents = []

    # Current position in tex content
    tex_content_position = 0

    # Construct a dictionary of index position to entry
    index_position_to_entry = construct_index_position_to_entry(tex_content)

    for index_position, index_entry in index_position_to_entry.items():

        # Get the tex content
        partial_tex_content = tex_content[tex_content_position:index_position]

        # Encode the exercise number into JSON string
        json_str = json.dumps({"index_entry": index_entry})

        # Create magic comment
        magic_comment = f"{INDEX_MAGIC_COMMENT_PREFIX} {json_str}\n"

        # Add both the partial tex content and the magic comment
        new_tex_contents.append(partial_tex_content)
        new_tex_contents.append(magic_comment)

        # Update tex content position
        tex_content_position = index_position

    # Add the rest of tex content to new tex contents
    new_tex_contents.append(tex_content[tex_content_position:])

    # Concatenate the new tex contents
    new_tex_content = "".join(new_tex_contents)

    return new_tex_content


def is_index_magic_comment(magic_comment: str) -> bool:
    """Check if the magic comment is an index magic comment.

    Parameters
    ----------
    magic_comment : str
        The magic comment.

    Returns
    -------
    bool
        Whether the magic comment is an index magic comment.
    """

    return magic_comment.startswith(INDEX_MAGIC_COMMENT_PREFIX)


def extract_index_entry(index_magic_comment: str) -> str:
    """Extract the index entry from the index magic comment.

    Parameters
    ----------
    index_magic_comment : str
        The magic comment of the index entry.

    Returns
    -------
    str
        The index entry.
    """

    # Get the JSON string
    json_string = index_magic_comment.removeprefix(INDEX_MAGIC_COMMENT_PREFIX).strip()

    # Parse the JSON string
    index_entry_dict: dict[str, str] = json.loads(json_string)

    # Get the index entry
    index_entry = index_entry_dict["index_entry"]

    return index_entry


def construct_index_position_to_entry(tex_content: str) -> dict[int, str]:

    # A dictionary of index position to entry
    index_position_to_entry: dict[int, str] = {}

    # The last desired match
    last_desired_match = None

    for index_match in INDEX_RE.finditer(tex_content):

        # The starting position from which we want to search for the matches
        start_position = 0 if last_desired_match is None else last_desired_match.start()

        # Find the last double newline before this index
        double_newlines_matches = list(
            DOUBLE_NEWLINES_RE.finditer(
                tex_content,
                pos=start_position,
                endpos=index_match.start(),
            )
        )
        double_newlines_match = (
            None if len(double_newlines_matches) == 0 else double_newlines_matches[-1]
        )

        # Find the last section before this index
        section_matches = list(
            SECTION_RE.finditer(
                tex_content,
                pos=start_position,
                endpos=index_match.start(),
            )
        )
        section_match = None if len(section_matches) == 0 else section_matches[-1]

        # Find the last chapter before this index
        chapter_matches = list(
            CHAPTER_RE.finditer(
                tex_content,
                pos=start_position,
                endpos=index_match.start(),
            )
        )
        chapter_match = None if len(chapter_matches) == 0 else chapter_matches[-1]

        # Get non-null matches
        matches = list(
            filter(
                lambda match: match is not None,
                [
                    double_newlines_match,
                    section_match,
                    chapter_match,
                ],
            )
        )

        # If there is no match, raise an error
        if len(matches) == 0:
            raise ValueError("No matches")

        # Get the mathch that has the largest end
        desired_match = sorted(
            matches,
            key=lambda x: x.end(),
        )[-1]

        # Update last desired match
        last_desired_match = desired_match

        # Index position
        index_position = desired_match.end()

        # Get index entry
        index_entry = index_match.group()[len(r"\index{") : -1]

        # Assign entry to index position
        index_position_to_entry[index_position] = index_entry

    return index_position_to_entry
