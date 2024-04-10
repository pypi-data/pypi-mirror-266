from pydantic import BaseModel


class Tex(BaseModel):

    macros: dict[str, str | list[str | int]] = {}


class Mathjax3Config(BaseModel):

    tex: Tex = Tex()


class SphinxConfig(BaseModel):

    mathjax3_config: Mathjax3Config = Mathjax3Config()
