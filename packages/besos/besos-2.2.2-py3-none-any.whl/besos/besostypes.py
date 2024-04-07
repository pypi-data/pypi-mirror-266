"""Type definitions used for BESOS' type hints.

PathLike is defined a any object implementing ``os.pathlike`` or a string.
It is an alias for ``Union[os.PathLike, str]``
"""

# Python Core Libraries
import os
from typing import Union


PathLike = Union[os.PathLike, str]
