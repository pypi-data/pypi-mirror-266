from pydantic import BaseModel


class HTMLSettings(BaseModel):

    # A path to a favicon image
    favicon: str = ""

    # Whether to add an "edit this page" button to pages. If `true`, repository information in repository: must be filled in
    use_edit_page_button: bool = False

    # Whether to add a link to your repository button
    use_repository_button: bool = False

    # Whether to add an "open an issue" button
    use_issues_button: bool = False

    # Continuous numbering across parts/chapters
    use_multitoc_numbering: bool = True

    # Will be displayed underneath the footer.
    extra_footer: str = ""

    # A GA id that can be used to track book views.
    google_analytics_id: str = ""

    # Whether to include your home page in the left Navigation Bar
    home_page_in_navbar: bool = True

    # The base URL where your book will be hosted. Used for creating image previews and social links. e.g.: https://mypage.com/mybook/
    baseurl: str = ""

    # Analytics configuration
    analytics: dict = {}

    # Comments configuration
    comments: dict = {"hypothesis": False, "utterances": False}

    # A banner announcement at the top of the site.
    announcement: str = ""
