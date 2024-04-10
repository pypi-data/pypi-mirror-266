import re
from typing import Optional
from TexSoup.utils import Token

from ..context import Context


def tex_token_to_markdown(
    token: Token,
    *,
    context: Optional[Context] = None,
) -> str:

    # Remove repeated whitespaces
    markdown_content = re.sub(r" +", " ", str(token))

    return markdown_content
