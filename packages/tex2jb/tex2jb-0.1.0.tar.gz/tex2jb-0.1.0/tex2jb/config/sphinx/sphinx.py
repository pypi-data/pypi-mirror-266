from pydantic import BaseModel

from .config import SphinxConfig


class SphinxSettings(BaseModel):

    # A list of extra extensions to load by Sphinx (added to those already used by JB)
    extra_extensions: list[str] = []

    # A list of local extensions to load by sphinx specified by "name: path" items
    local_extensions: dict[str, str] = {}

    # A boolean indicating whether to overwrite the Sphinx config (true) or recursively update (false)
    recursive_update: bool = False

    # Key-value pairs to directly over-ride the Sphinx configuration
    config: SphinxConfig = SphinxConfig()
