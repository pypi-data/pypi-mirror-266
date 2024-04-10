from typing import Optional
from TexSoup.utils import Token

from ..context import Context
from ..magic_comments import is_index_magic_comment, extract_index_entry


def comment_to_markdown(
    comment_token: Token,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the comment token to markdown.
    The normal LaTeX comments should be ignored.
    However, if it is a magic comment, it should be converted to markdown.

    Parameters
    ----------
    comment_token : Token
        The comment token.

    Returns
    -------
    str
        The markdown representation of the comment.
        An empty string for a normal LaTeX comment.
        An associated markdown comment for a magic comment.
    """

    comment = str(comment_token)

    if is_index_magic_comment(comment):

        # Get index entry
        index_entry = extract_index_entry(comment)

        # Markdown associated with the index entry
        # It is a directive
        return f"```{{index}} {index_entry}\n```\n"

    return ""
