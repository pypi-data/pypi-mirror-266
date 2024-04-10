from pydantic import BaseModel


class LatexSettings(BaseModel):

    # One of 'pdflatex', 'xelatex' (recommended for unicode), 'luatex', 'platex', 'uplatex'
    latex_engine: str = "pdflatex"

    # Use sphinx-jupyterbook-latex for pdf builds as default
    use_jupyterbook_latex: bool = True
