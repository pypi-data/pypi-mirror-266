import re
from TexSoup import TexNode
from TexSoup.utils import Token
from TexSoup.data import TexNamedEnv

from .tex_element_type import TexElementType


def get_tex_element_type(tex_element: TexNode | Token) -> TexElementType:

    if isinstance(tex_element, Token):

        if is_comment(tex_element):
            return TexElementType.COMMENT

        return TexElementType.TOKEN

    assert isinstance(
        tex_element, TexNode
    ), f"Unknown tex element type: {type(tex_element)}"

    if is_frontmatter(tex_element):
        return TexElementType.FRONTMATTER

    if is_mainmatter(tex_element):
        return TexElementType.MAINMATTER

    if is_tableofcontents(tex_element):
        return TexElementType.TABLEOFCONTENTS

    if is_part(tex_element):
        return TexElementType.PART

    if is_chapter(tex_element):
        return TexElementType.CHAPTER

    if is_section(tex_element):
        return TexElementType.SECTION

    if is_subsection(tex_element):
        return TexElementType.SUBSECTION

    if is_text(tex_element):
        return TexElementType.TEXT

    if is_textbf(tex_element):
        return TexElementType.TEXTBF

    if is_textit(tex_element):
        return TexElementType.TEXTIT

    if is_texttt(tex_element):
        return TexElementType.TEXTTT

    if is_label(tex_element):
        return TexElementType.LABEL

    if is_index(tex_element):
        return TexElementType.INDEX

    if is_ref(tex_element):
        return TexElementType.REF

    if is_eqref(tex_element):
        return TexElementType.EQREF

    if is_cite(tex_element):
        return TexElementType.CITE

    if is_enumerate(tex_element):
        return TexElementType.ENUMERATE

    if is_figure(tex_element):
        return TexElementType.FIGURE

    if is_align(tex_element):
        return TexElementType.ALIGN

    if is_theorem(tex_element):
        return TexElementType.THEOREM

    if is_definition(tex_element):
        return TexElementType.DEFINITION

    if is_proposition(tex_element):
        return TexElementType.PROPOSITION

    if is_lemma(tex_element):
        return TexElementType.LEMMA

    if is_corollary(tex_element):
        return TexElementType.COROLLARY

    if is_example(tex_element):
        return TexElementType.EXAMPLE

    if is_proof(tex_element):
        return TexElementType.PROOF

    if is_note(tex_element):
        return TexElementType.NOTE

    if is_exercise(tex_element):
        return TexElementType.EXERCISE

    if is_solution(tex_element):
        return TexElementType.SOLUTION

    if is_printbibliography(tex_element):
        return TexElementType.PRINTBIBLIOGRAPHY

    if is_printindex(tex_element):
        return TexElementType.PRINTINDEX


def is_comment(tex_token: Token) -> bool:

    return re.match(r"^%.*$", tex_token) is not None


def is_frontmatter(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "frontmatter"


def is_mainmatter(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "mainmatter"


def is_tableofcontents(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "tableofcontents"


def is_part(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "part"


def is_chapter(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name in {"chapter", "chapter*"}


def is_section(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name in {"section", "section*"}


def is_subsection(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name in {"subsection", "subsection*"}


def is_text(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "text"


def is_textbf(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "textbf"


def is_textit(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "textit"


def is_texttt(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "texttt"


def is_label(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "label"


def is_index(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "index"


def is_ref(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "ref"


def is_eqref(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "eqref"


def is_cite(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "cite"


def is_enumerate(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "enumerate"


def is_figure(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "figure"


def is_align(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name in {"align", "align*"}


def is_theorem(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "theorem"


def is_definition(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "definition"


def is_proposition(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "proposition"


def is_lemma(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "lemma"


def is_corollary(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "corollary"


def is_example(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "example"


def is_proof(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "proof"


def is_note(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "note"


def is_exercise(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "exercise"


def is_solution(tex_node: TexNode) -> bool:

    # Get the name of the environment
    environment_name = tex_node.expr.name

    return environment_name == "solution"


def is_printbibliography(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "printbibliography"


def is_printindex(tex_node: TexNode) -> bool:

    # Get the name of the command
    command_name = tex_node.expr.name

    return command_name == "printindex"
