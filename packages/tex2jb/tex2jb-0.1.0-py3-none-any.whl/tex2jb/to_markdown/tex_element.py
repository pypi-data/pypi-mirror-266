from typing import Optional
from TexSoup import TexNode
from TexSoup.data import Token

from ..context import Context
from ..tex_element_type import TexElementType, get_tex_element_type


def tex_elements_to_markdown(
    tex_elements: list[TexNode | Token],
    *,
    context: Optional[Context] = None,
) -> str:

    # All markdown contents of the tex elements
    markdown_contents: list[str] = []

    # Collect each markdown content
    for tex_element in tex_elements:

        # Markdown of the tex element
        content = tex_element_to_markdown(tex_element, context=context)

        # Collect the content
        markdown_contents.append(content)

    # Join the markdown contents
    markdown_content = "".join(markdown_contents)

    return markdown_content


def tex_element_to_markdown(
    tex_element: TexNode | Token,
    *,
    context: Optional[Context] = None,
) -> str:

    # * Import the corresponding function for the tex element type here in the function body
    # * to avoid circular import errors
    from .comment import comment_to_markdown
    from .frontmatter import frontmatter_to_markdown
    from .mainmatter import mainmatter_to_markdown
    from .tableofcontents import tableofcontents_to_markdown
    from .part import part_to_markdown
    from .chapter import chapter_to_markdown
    from .section import section_to_markdown
    from .subsection import subsection_to_markdown
    from .text import text_to_markdown
    from .textbf import textbf_to_markdown
    from .textit import textit_to_markdown
    from .texttt import texttt_to_markdown
    from .align import align_to_markdown
    from .tex_token import tex_token_to_markdown
    from .label import label_to_markdown
    from .index import index_to_markdown
    from .ref import ref_to_markdown
    from .eqref import eqref_to_markdown
    from .cite import cite_to_markdown
    from .enumerate import enumerate_to_markdown
    from .figure import figure_to_markdown
    from .theorem import theorem_to_markdown
    from .definition import definition_to_markdown
    from .proposition import proposition_to_markdown
    from .lemma import lemma_to_markdown
    from .corollary import corollary_to_markdown
    from .example import example_to_markdown
    from .proof import proof_to_markdown
    from .note import note_to_markdown
    from .exercise import exercise_to_markdown
    from .solution import solution_to_markdown
    from .printbibliography import printbibliography_to_markdown
    from .printindex import printindex_to_markdown

    # Infer the tex element type
    tex_element_type = get_tex_element_type(tex_element)

    # Convert the tex element to markdown
    match tex_element_type:
        case TexElementType.COMMENT:
            content = comment_to_markdown(tex_element, context=context)

        case TexElementType.TOKEN:
            content = tex_token_to_markdown(tex_element, context=context)

        case TexElementType.FRONTMATTER:
            content = frontmatter_to_markdown(tex_element, context=context)

        case TexElementType.MAINMATTER:
            content = mainmatter_to_markdown(tex_element, context=context)

        case TexElementType.TABLEOFCONTENTS:
            content = tableofcontents_to_markdown(tex_element, context=context)

        case TexElementType.PART:
            content = part_to_markdown(tex_element, context=context)

        case TexElementType.CHAPTER:
            content = chapter_to_markdown(tex_element, context=context)

        case TexElementType.SECTION:
            content = section_to_markdown(tex_element, context=context)

        case TexElementType.SUBSECTION:
            content = subsection_to_markdown(tex_element, context=context)

        case TexElementType.TEXT:
            content = text_to_markdown(tex_element, context=context)

        case TexElementType.TEXTBF:
            content = textbf_to_markdown(tex_element, context=context)

        case TexElementType.TEXTIT:
            content = textit_to_markdown(tex_element, context=context)

        case TexElementType.TEXTTT:
            content = texttt_to_markdown(tex_element, context=context)

        case TexElementType.LABEL:
            content = label_to_markdown(tex_element, context=context)

        case TexElementType.INDEX:
            content = index_to_markdown(tex_element, context=context)

        case TexElementType.REF:
            content = ref_to_markdown(tex_element, context=context)

        case TexElementType.EQREF:
            content = eqref_to_markdown(tex_element, context=context)

        case TexElementType.CITE:
            content = cite_to_markdown(tex_element, context=context)

        case TexElementType.ENUMERATE:
            content = enumerate_to_markdown(tex_element, context=context)

        case TexElementType.FIGURE:
            content = figure_to_markdown(tex_element, context=context)

        case TexElementType.ALIGN:
            content = align_to_markdown(tex_element, context=context)

        case TexElementType.THEOREM:
            content = theorem_to_markdown(tex_element, context=context)

        case TexElementType.DEFINITION:
            content = definition_to_markdown(tex_element, context=context)

        case TexElementType.PROPOSITION:
            content = proposition_to_markdown(tex_element, context=context)

        case TexElementType.LEMMA:
            content = lemma_to_markdown(tex_element, context=context)

        case TexElementType.COROLLARY:
            content = corollary_to_markdown(tex_element, context=context)

        case TexElementType.EXAMPLE:
            content = example_to_markdown(tex_element, context=context)

        case TexElementType.PROOF:
            content = proof_to_markdown(tex_element, context=context)

        case TexElementType.NOTE:
            content = note_to_markdown(tex_element, context=context)

        case TexElementType.EXERCISE:
            content = exercise_to_markdown(tex_element, context=context)

        case TexElementType.SOLUTION:
            content = solution_to_markdown(tex_element, context=context)

        case TexElementType.PRINTBIBLIOGRAPHY:
            content = printbibliography_to_markdown(tex_element, context=context)

        case TexElementType.PRINTINDEX:
            content = printindex_to_markdown(tex_element, context=context)

        case _:
            content = str(tex_element)

    return content
