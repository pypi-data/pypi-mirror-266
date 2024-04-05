"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from os import stat_result
from pathlib import Path
from typing import Optional

from .common import PATHABLE
from .match import rgxp_match



_REPLACE = dict[str, str]



def resolve_path(
    path: str | Path,
    replace: Optional[_REPLACE] = None,
) -> Path:
    """
    Resolve the provided path and replace the magic keywords.

    Example
    -------
    >>> resolve_path('/foo/bar')
    PosixPath('/foo/bar')

    :param path: Complete or relative path for processing.
    :param replace: Optional string values to replace in path.
    :returns: New resolved filesystem path object instance.
    """

    path = str(path).strip()

    if replace is not None:
        for old, new in replace.items():
            path = path.replace(old, new)

    return Path(path).resolve()



def resolve_paths(
    paths: PATHABLE,
    replace: Optional[_REPLACE] = None,
) -> tuple[Path, ...]:
    """
    Resolve the provided paths and replace the magic keywords.

    .. note::
       This will remove duplicative paths from the returned.

    Example
    -------
    >>> resolve_paths(['/foo/bar'])
    (PosixPath('/foo/bar'),)

    :param paths: Complete or relative paths for processing.
    :param replace: Optional string values to replace in path.
    :returns: New resolved filesystem path object instances.
    """

    returned: list[Path] = []

    if isinstance(paths, str | Path):
        paths = [paths]

    for path in paths:

        _path = resolve_path(
            str(path), replace)

        if _path in returned:
            continue

        returned.append(_path)

    return tuple(returned)



def stats_path(
    path: str | Path,
    replace: Optional[_REPLACE] = None,
    ignore: Optional[list[str]] = None,
) -> dict[str, stat_result]:
    """
    Collect stats object for the complete or relative path.

    .. testsetup::
       >>> path = Path(getfixture('tmpdir'))
       >>> file = path.joinpath('hello.txt')
       >>> file.write_text('Hello world!')
       12

    Example
    -------
    >>> replace = {str(path): '/'}
    >>> stats = stats_path(path, replace)
    >>> stats['/hello.txt'].st_size
    12

    :param path: Complete or relative path for enumeration.
    :param replace: Optional string values to replace in path.
    :param ignore: Paths matching these patterns are ignored.
    :returns: Metadata for files recursively found in path.
    """

    path = Path(path).resolve()

    returned: dict[str, stat_result] = {}


    def _ignore() -> bool:
        assert ignore is not None
        return rgxp_match(
            str(item), ignore)


    for item in path.iterdir():

        if ignore and _ignore():
            continue

        if item.is_dir():

            meta = stats_path(
                item, replace, ignore)

            returned.update(meta)

        elif item.is_file():

            key = resolve_path(
                item, replace)

            returned[str(key)] = (
                item.stat())


    return dict(sorted(returned.items()))
