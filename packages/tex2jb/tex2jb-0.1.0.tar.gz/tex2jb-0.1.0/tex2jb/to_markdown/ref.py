from typing import Optional
from TexSoup import TexNode

from ..context import Context


# If the label mark starts with any of the following prefixes,
# the markdown content will be {prf:ref}`<label marker>`,
# which is the syntax of the Sphinx Proof
SPHINX_PROOF_LABEL_MARKER_PREFIXES = (
    "thm",
    "def",
    "prop",
    "pro",
    "lem",
    "cor",
    "eg",
)

# The prefix of the exercise label marker
EXERCISE_LABEL_MARKER_PREFIX = "ex"

# The prefix of the figure label marker
FIGURE_LABEL_MARKER_PREFIX = "fig"


def ref_to_markdown(
    ref_node: TexNode,
    *,
    context: Optional[Context] = None,
) -> str:
    """Convert the ref node to markdown.
    If the label marker starts with any of the Sphinx Proof label marker prefixes,
    the markdown content will be {prf:ref}`<label marker>`.
    Otherwise, the markdown content will be {ref}`<label marker>`.

    Parameters
    ----------
    ref_node : TexNode
        The ref node.

    Returns
    -------
    str
        The markdown representation of the ref command.
    """

    # Get label marker
    label_marker: str = str(ref_node.args[0].string)

    # Sphinx Proof label marker
    for prefix in SPHINX_PROOF_LABEL_MARKER_PREFIXES:

        if label_marker.startswith(prefix):

            # Markdown content
            return f"{{prf:ref}}`{label_marker}`"

    # * The reference to an exercise needs to be handled specifically, which requires the context
    if EXERCISE_LABEL_MARKER_PREFIX in label_marker:

        assert context is not None, "The context is not found"

        # Get the exercise number
        exercise_number = context.exercise_label_marker_to_number[label_marker]

        # Markdown content
        return f"[Exercise {exercise_number}]({label_marker})"

    if FIGURE_LABEL_MARKER_PREFIX in label_marker:

        # * Use numbered ref for figures
        # Reference: https://jupyterbook.org/en/stable/content/figures.html#numbered-references
        return f"{{numref}}`{label_marker}`"

    # Markdown content
    return f"{{ref}}`{label_marker}`"
