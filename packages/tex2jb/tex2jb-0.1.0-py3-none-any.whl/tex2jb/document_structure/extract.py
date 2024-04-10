from typing import Optional
from pathlib import Path
from TexSoup import TexNode
from TexSoup.utils import Token

from .part import Part
from .chapter import Chapter
from .section import Section
from .table_of_contents import TableOfContents
from ..tex_element_type import TexElementType, get_tex_element_type


PRINTBIBLIOGRAPHY_COMMAND_NAME = "printbibliography"
PRINTINDEX_COMMAND_NAME = "printindex"

BIBLIOGRAPHY_FILE_PATH = Path("bibliography.md")

INTRO_FILE_PATH = Path("intro.md")

# This special name is defined by Jupyter Book
# Reference: https://jupyterbook.org/en/stable/content/content-blocks.html#add-the-general-index-to-your-table-of-contents
INDEX_FILE_PATH = Path("genindex.md")


def extract_document_structure(
    document_node: TexNode,
    intro_path: str,
) -> tuple[TableOfContents, dict[Path, list[TexNode | Token]]]:

    parts: list[Part] = []
    main_matter_parts: list[Part] = []
    front_matter_part: Optional[Part] = None
    part: Optional[Part] = None

    chapters: list[Chapter] = []
    chapter: Optional[Chapter] = None

    file_path_to_tex_elements: dict[Path, list[TexNode | Token]] = {}
    file_path: Optional[Path] = None

    # \printbibliography node
    printbibliography_node: Optional[TexNode] = None

    # \printindex node
    printindex_node: Optional[TexNode] = None

    for element in document_node.contents:

        # Get the type of the element
        element_type = get_tex_element_type(element)

        match element_type:

            case TexElementType.FRONTMATTER:

                # Create a part for front matter
                part = Part(
                    caption=None,
                    numbered=False,
                    chapters=[],
                )

                # Add the part
                parts.append(part)

            case TexElementType.MAINMATTER:

                # Reset the current part to None
                part = None

            case TexElementType.PART:

                # Get the caption of the part
                part_caption = element.args[0].string

                # Create the part
                part = Part(
                    caption=part_caption,
                    # We want the chapters and sections in the part to be numbered
                    numbered=True,
                    chapters=[],
                )

                # Add the part
                main_matter_parts.append(part)

            case TexElementType.CHAPTER:

                # Get the title of the chapter
                chapter_title = element.args[0].string

                # The file path for the chapter is special
                # It is the index page of the chapter directory
                file_path = Path(chapter_title).joinpath("index.md")

                # Create the chapter
                chapter = Chapter(
                    title=chapter_title,
                    file_path=file_path,
                    sections=[],
                )

                # Initialize the list of tex elements associated with this file path
                file_path_to_tex_elements[file_path] = []

                # Add the chapter

                # There is no part
                if part is None:
                    chapters.append(chapter)

                # Assign the chapter to the current part
                else:
                    part.chapters.append(chapter)

            case TexElementType.SECTION:

                # Check if the current chapter is not None
                assert chapter is not None, "The current chapter is None"

                # Get the title of the section
                section_title = element.args[0].string

                # Path of the section markdown file
                file_path = Path(chapter.title).joinpath(section_title + ".md")

                # Create the section
                section = Section(
                    title=section_title,
                    file_path=file_path,
                )

                # Add the section to the current chapter
                chapter.sections.append(section)

                # Initialize the list of tex elements associated with this file path
                file_path_to_tex_elements[file_path] = []

            # Don't collect \printbibliography node for now
            # It will be handled later
            case TexElementType.PRINTBIBLIOGRAPHY:
                printbibliography_node = element
                continue

            # Don't collect \printindex node for now
            # It will be handled later
            case TexElementType.PRINTINDEX:
                printindex_node = element
                continue

            case _:
                pass

        if file_path not in file_path_to_tex_elements:
            continue

        # Assign the element to the current file path
        tex_elements = file_path_to_tex_elements[file_path]
        tex_elements.append(element)

    # ------------
    # Front Matter
    # ------------

    # -----------
    # Main Matter
    # -----------

    # Add the front matter parts to parts
    parts.extend(main_matter_parts)

    # There are no parts in the document
    # Create a dummy part to hold the chapters
    if len(main_matter_parts) == 0:
        dummy_part = Part(
            # No caption
            caption=None,
            # We want the chapters and sections in the part to be numbered
            numbered=True,
            chapters=chapters,
        )
        parts.append(dummy_part)

    # --------
    # Appendix
    # --------

    # Create an appendix part
    appendix_part = Part(
        caption="Appendix",
        numbered=False,
        chapters=[],
    )

    # Bibliography
    if printbibliography_node is not None:

        bibliography_chapter = Chapter(
            title="Bibliography",
            file_path=BIBLIOGRAPHY_FILE_PATH,
            sections=[],
        )

        # Add to the appendix part
        appendix_part.chapters.append(bibliography_chapter)

        # Assign \printbibliography node to the bibliography chapter
        file_path_to_tex_elements[BIBLIOGRAPHY_FILE_PATH] = [printbibliography_node]

    # Index
    if printindex_node is not None:

        index_chapter = Chapter(
            title="Index",
            file_path=INDEX_FILE_PATH,
            sections=[],
        )

        # Add to the appendix part
        appendix_part.chapters.append(index_chapter)

        # Assign \printindex node to the index chapter
        file_path_to_tex_elements[INDEX_FILE_PATH] = [printindex_node]

    # Add the appendix part if its chapters are not empty
    if len(appendix_part.chapters) > 0:
        parts.append(appendix_part)

    # -----------------
    # Table of Contents
    # -----------------

    # Create the table of contents
    table_of_contents = TableOfContents(
        format="jb-book",
        root=intro_path,
        parts=parts,
    )

    return (
        table_of_contents,
        file_path_to_tex_elements,
    )
