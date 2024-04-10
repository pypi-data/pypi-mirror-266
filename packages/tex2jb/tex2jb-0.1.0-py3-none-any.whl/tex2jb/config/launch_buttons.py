from pydantic import BaseModel


class LaunchButtonsSettings(BaseModel):

    # The interface interactive links will activate ["classic", "jupyterlab"]
    notebook_interface: str = "classic"

    # The URL of the BinderHub (e.g., https://mybinder.org)
    binderhub_url: str = ""

    # The URL of the JupyterHub (e.g., https://datahub.berkeley.edu)
    jupyterhub_url: str = ""

    # Add a thebe button to pages (requires the repository to run on Binder)
    thebe: bool = False

    # Google Colab URL
    colab_url: str = ""
