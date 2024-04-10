from pydantic import BaseModel


class ExecutionSettings(BaseModel):

    # Whether to execute notebooks at build time. Must be one of ("auto", "force", "cache", "off")
    execute_notebooks: str = "auto"

    # A path to the jupyter cache that will be used to store execution artifacts. Defaults to `_build/.jupyter_cache/`
    cache: str = ""

    # A list of patterns to *skip* in execution (e.g. a notebook that takes a really long time)
    exclude_patterns: list[str] = []

    # The maximum time (in seconds) each notebook cell is allowed to run
    timeout: int = 30

    # If `True`, then a temporary directory will be created and used as the command working directory (cwd),
    # otherwise the notebook's parent directory will be the cwd.
    run_in_temp: bool = False

    # If `False`, when a code cell raises an error the execution is stopped, otherwise all cells are always run
    allow_errors: bool = False

    # One of 'show', 'remove', 'remove-warn', 'warn', 'error', 'severe'
    stderr_output: str = "show"
