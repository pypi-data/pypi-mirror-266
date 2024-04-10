"""
`embedops_cli`
=======================================================================
"""

# check compatibility
import sys
import platform

from .version import (
    __version__,
)  # Import __version__ attribute so that it is visible to the setup.cfg

MIN_PYTHON_VERSION = (3, 9)


def _check_valid_python_version():
    if sys.version_info < MIN_PYTHON_VERSION:
        print(
            f"EmbedOps CLI requires Python {MIN_PYTHON_VERSION[0]}."
            f"{MIN_PYTHON_VERSION[1]} or higher.\n",
            f"Your version is {platform.python_version()}.\n",
            "Please upgrade your Python installation.\n",
        )
        sys.exit(1)


# We are using language features that are syntax errors in python before 3.9
# We need to check the python version before we import or process any code
# that causes a syntax error, so do it here in __init__.py
# Tested with a 3.8 venv and it fails gracefully printing the expected message
_check_valid_python_version()
