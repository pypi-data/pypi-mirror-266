"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from typing import Union



JOINABLE = (list, tuple, set)



PATHABLE = Union[
    str, Path,
    list[str | Path],
    tuple[str | Path],
    set[str]]



REPLACE = Union[
    dict[str, str],
    dict[str, str | Path],
    dict[str, Path],
    dict[str, str],
    dict[str | Path, str],
    dict[Path, str]]



def read_text(
    path: str | Path,
) -> str:
    """
    Read the text content from within the provided file path.

    :param path: Complete or relative path to the text file.
    :returns: Text content that was read from the file path.
    """

    path = Path(path).resolve()

    return path.read_text(
        encoding='utf-8')



def save_text(
    path: str | Path,
    content: str,
) -> str:
    """
    Save the provided text content to the provided file path.

    :param path: Complete or relative path to the text file.
    :param content: Content that will be written to the file.
    :returns: Text content that was read from the file path.
    """

    path = Path(path).resolve()

    path.write_text(
        data=content,
        encoding='utf-8')

    return read_text(path)
