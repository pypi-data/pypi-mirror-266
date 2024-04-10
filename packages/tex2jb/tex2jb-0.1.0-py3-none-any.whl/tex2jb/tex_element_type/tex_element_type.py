from enum import Enum, auto


class TexElementType(Enum):

    TOKEN = auto()

    COMMENT = auto()

    FRONTMATTER = auto()
    MAINMATTER = auto()

    TABLEOFCONTENTS = auto()

    PART = auto()
    CHAPTER = auto()
    SECTION = auto()
    SUBSECTION = auto()

    TEXT = auto()
    TEXTBF = auto()
    TEXTIT = auto()
    TEXTTT = auto()

    LABEL = auto()

    INDEX = auto()

    REF = auto()
    EQREF = auto()

    CITE = auto()

    ENUMERATE = auto()

    FIGURE = auto()

    ALIGN = auto()

    THEOREM = auto()
    DEFINITION = auto()
    PROPOSITION = auto()
    LEMMA = auto()
    COROLLARY = auto()
    EXAMPLE = auto()
    PROOF = auto()

    NOTE = auto()
    EXERCISE = auto()
    SOLUTION = auto()

    PRINTBIBLIOGRAPHY = auto()
    PRINTINDEX = auto()
