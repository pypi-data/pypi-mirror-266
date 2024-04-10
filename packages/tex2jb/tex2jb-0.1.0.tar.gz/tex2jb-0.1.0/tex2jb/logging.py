import logging
from rich.logging import RichHandler

# The logger of this project
logger = logging.getLogger("tex2jb")

# Logging formatter
# * We only show the message here
# * since other information will already be shown in the rich handler
formatter = logging.Formatter(
    "%(message)s",
)

# Rich handler
handler = RichHandler(
    # Don't show the file path
    show_path=False,
    rich_tracebacks=True,
)

# Set the formatter for the handler
handler.setFormatter(formatter)

# Set the logger
logger.setLevel(logging.INFO)
logger.addHandler(handler)
