from pydantic import BaseModel


class ParseSettings(BaseModel):

    # Default extensions to enable in the myst parser.
    # See https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html
    myst_enable_extensions: list[str] = [
        "colon_fence",
        "dollarmath",
        "linkify",
        "substitution",
        "tasklist",
    ]

    # URI schemes that will be recognised as external URLs in Markdown links
    myst_url_schemes: list[str] = ["mailto", "http", "https"]

    # Allow display math ($$) within an inline context
    myst_dmath_double_inline: bool = True
