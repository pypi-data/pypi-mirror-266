import re

TILDE_SUFFIX_RE = re.compile(r"\w*~")


def remomve_words_with_tilde_suffix(tex_content: str) -> str:
    """Remove all the words with tilde(~) suffixes in the tex content.
    For example, `Theorem~` will be removed from `Theorem~\ref{thm:1}`.

    Parameters
    ----------
    tex_content : str
        Original tex content.

    Returns
    -------
    str
        Tex content with these words removed.
    """

    return TILDE_SUFFIX_RE.sub("", tex_content)
