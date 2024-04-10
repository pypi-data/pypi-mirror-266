import subprocess
from typing import Optional
from pathlib import Path
import shutil
import yaml
import typer
from TexSoup import TexNode

from .app import app
from tex2jb.logging import logger
from tex2jb.preprocessing import preprocess_tex
from tex2jb.config import SimplifiedBookSettings, BookSettings
from tex2jb.logo import find_logo_and_favicon
from tex2jb.intro import create_intro_markdown
from tex2jb.document_structure import extract_document_structure
from tex2jb.to_markdown import tex_elements_to_markdown
from tex2jb.static import create_static_dir

# The largest logging level is CRITICAL (50)
# Reference: https://docs.python.org/3/library/logging.html#logging-levels
QUIET_LEVEL = 60

BOOK_SETTINGS_FILE_NAME = Path("_config.yml")
TABLE_OF_CONTENTS_FILE_NAME = Path("_toc.yml")


@app.command()
def convert(
    tex_path: Path = typer.Argument(
        show_default=False,
        help="The path to the tex file to convert.",
    ),
    book_dir: Path = typer.Argument(
        show_default=False,
        help="Root directory of the Jupyter Book contents to generate.",
    ),
    github_url: Optional[str] = typer.Option(
        None,
        "-g",
        "--github",
        help="The GitHub URL to the book's repository.",
    ),
    tex_macros_path: Optional[Path] = typer.Option(
        None,
        "-m",
        "--tex-macros",
        help="The path to the custom tex macros file (YAML).",
    ),
    force_config: bool = typer.Option(
        False,
        help="Overwrite the existing book settings if it exists.",
    ),
    jb: bool = typer.Option(
        True,
        help="Run Jupyter Book to build HTML pages after the conversion is finished. Note that command `jb clean -a <book_dir>` will be run before running `jb build <book_dir>` to clean up previous Jupyter Book outputs.",
    ),
    quiet: bool = typer.Option(
        False,
        help="Suppress output.",
    ),
):

    # Suppress output
    if quiet:
        logger.setLevel(QUIET_LEVEL)

    # Convert to absolute path
    tex_path = tex_path.absolute()
    book_dir = book_dir.absolute()

    # * Remove all subdirectories in the book directory
    for subdir in book_dir.iterdir():
        if subdir.is_dir():
            shutil.rmtree(subdir)

    # Log
    logger.info(f"Cleaned up all subdirectories in {book_dir}")

    # -------------
    # Preprocessing
    # -------------

    # Read tex content
    tex_content = tex_path.read_text()

    # Preprocess tex content and get the root node and the context
    root_node, context = preprocess_tex(tex_content)

    # Set context
    context.tex_path = tex_path
    context.book_dir = book_dir

    # --------------------
    # Creating _static Dir
    # --------------------

    create_static_dir(book_dir)

    # -------------
    # Book Settings
    # -------------

    # Write book settings if it does not exist, or
    # it is requested to be overwritten
    if force_config or not book_dir.joinpath(BOOK_SETTINGS_FILE_NAME).is_file():
        write_book_settings(
            root_node=root_node,
            tex_path=tex_path,
            book_dir=book_dir,
            github_url=github_url,
            tex_macros_path=tex_macros_path,
        )
    else:
        logger.info(
            f"Using the existing book settings at {book_dir.joinpath(BOOK_SETTINGS_FILE_NAME)}"
        )

    # ----------------------------------------
    # Document Structure and Table of Contents
    # ----------------------------------------

    # Get the document node
    document_node: Optional[TexNode] = root_node.find("document")
    assert document_node is not None, "The document node is not found"

    # Find the introduction file from _toc.yml
    intro_path: Optional[Path] = None
    if book_dir.joinpath(TABLE_OF_CONTENTS_FILE_NAME).is_file():

        with open(book_dir.joinpath(TABLE_OF_CONTENTS_FILE_NAME), "r") as f:
            intro_path = book_dir.joinpath(yaml.safe_load(f)["root"])

        # Log
        logger.info(f"Using the existing introduction file at {intro_path}")

    # Create intro markdown if it does not exist
    else:
        # Log
        logger.warning("No introduction file is found")

        # Get book title from settings
        with open(book_dir.joinpath(BOOK_SETTINGS_FILE_NAME), "r") as f:
            book_settings = BookSettings.model_validate(yaml.safe_load(f))
        book_title = book_settings.title

        # Create intro markdown
        intro_path = create_intro_markdown(
            book_dir=book_dir,
            book_title=book_title,
        )

        # Log
        logger.info(f"Created the introduction file at {intro_path}")

    assert intro_path is not None

    # Extract the document structure
    table_of_contents, file_path_to_tex_elements = extract_document_structure(
        document_node,
        # Convert to relative path
        intro_path=str(intro_path.relative_to(book_dir)),
    )

    # Write table of contents
    table_of_contents_path = book_dir.joinpath(TABLE_OF_CONTENTS_FILE_NAME)
    with open(table_of_contents_path, "w") as f:
        yaml.dump(table_of_contents.model_dump(), f)

    # ------------------------
    # Composing Markdown Files
    # ------------------------

    # Convert tex elements of each file to markdown content
    for file_path, tex_elements in file_path_to_tex_elements.items():
        file_path = book_dir.joinpath(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_content = tex_elements_to_markdown(tex_elements, context=context)
        with open(file_path, "w") as f:
            f.write(markdown_content)

    # ------------
    # Jupyter Book
    # ------------

    # Log
    logger.info("Building HTML pages using Jupyter Book CLI...")

    # Use Jupyter Book CLI to build HTML pages
    if jb:
        # Clean up previous build
        subprocess.run(["jb", "clean", "-a", book_dir], check=True)

        # Build
        subprocess.run(["jb", "build", book_dir], check=True)

    # Prompt that the all is done
    logger.info("Done")


def write_book_settings(
    *,
    root_node: TexNode,
    tex_path: Path,
    book_dir: Path,
    github_url: Optional[str] = None,
    tex_macros_path: Optional[Path] = None,
) -> None:

    # Find \title
    title_node: TexNode = root_node.find("title")
    try:
        assert title_node is not None
    except:
        logger.error("Failed to find \\title in the document")

    # Get book title
    title = str(title_node.string)

    # Find \author
    author_node: TexNode = root_node.find("author")
    try:
        assert author_node is not None
    except:
        logger.error("Failed to find \\author in the document")

    # Get the author
    author = str(author_node.string)

    # Find \addbibresource
    bib_files = []
    addbibresource_nodes: list[TexNode] = root_node.find_all("addbibresource")
    for addbibresource_node in addbibresource_nodes:
        # Get the file name
        bib_name = str(addbibresource_node.string)

        # Add to the list
        bib_files.append(bib_name)

        # Absolute path of the bib file in the parent directory of the tex file
        tex_bib_path = tex_path.parent.joinpath(bib_name).absolute()

        # Absolute path of the bib file in the Jupyter Book directory
        book_bib_path = book_dir.joinpath(bib_name).absolute()

        # Create the parent dir of bib file in the Jupyter Book directory
        book_bib_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the bib file to the Jupyter Book directory
        shutil.copy(tex_bib_path, book_bib_path)

        # Log
        logger.info(f"Copied {tex_bib_path} to {book_bib_path}")

    # Find logo and favicon
    logo_path, favicon_path = find_logo_and_favicon(book_dir)

    # Create simplified settings
    simplified_settings = SimplifiedBookSettings(
        title=title,
        author=author,
        bibtex_bibfiles=bib_files,
        # Get the relative path of the logo
        logo=str(logo_path.relative_to(book_dir)),
        # Get the relative path of the favicon
        html_favicon=str(favicon_path.relative_to(book_dir)),
        # If github_url is None, it will be set to an empty string ""
        repository_url=github_url if github_url is not None else "",
        # I need to use sphinx_proof module
        sphinx_extra_extensions=["sphinx_proof"],
        tex_macros_path=tex_macros_path,
    )

    # Construct book settings out of the simplified settings
    book_settings = simplified_settings.to_book_settings()

    # Write book settings
    with open(book_dir.joinpath(BOOK_SETTINGS_FILE_NAME), "w") as f:
        yaml.dump(book_settings.model_dump(), f)
