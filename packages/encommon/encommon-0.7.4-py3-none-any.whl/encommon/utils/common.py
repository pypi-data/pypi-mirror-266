"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from typing import Union



JOINABLE = (
    list  # type: ignore
    | tuple  # type: ignore
    | set)  # type: ignore



PATHABLE = Union[
    str,
    Path,
    list[str | Path],
    tuple[str | Path],
    set[str]]
