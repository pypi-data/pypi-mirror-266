from pydantic import BaseModel


class RepositorySettings(BaseModel):

    # The URL to your book's repository
    url: str = "https://github.com/executablebooks/jupyter-book"

    # A path to your book's folder, relative to the repository root
    path_to_book: str = ""

    # Which branch of the repository should be used when creating links
    branch: str = "master"
