"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from os import stat_result
from pathlib import Path
from typing import Optional
from typing import TYPE_CHECKING

from .match import rgxp_match
from ..types import sort_dict

if TYPE_CHECKING:
    from .common import PATHABLE
    from .common import REPLACE



STATS_PATH = dict[str, stat_result]



def resolve_path(
    path: str | Path,
    replace: Optional['REPLACE'] = None,
) -> Path:
    """
    Resolve the provided path replacing the magic keywords.

    Example
    -------
    >>> resolve_path('/foo/bar')
    PosixPath('/foo/bar')

    :param path: Complete or relative path for processing.
    :param replace: Optional values to replace in the path.
    :returns: New resolved filesystem path object instance.
    """

    path = str(path).strip()

    if replace is not None:

        items = replace.items()

        for old, new in items:

            if isinstance(old, Path):
                old = str(old)

            if isinstance(new, Path):
                new = str(new)

            path = path.replace(old, new)

    return Path(path).resolve()



def resolve_paths(
    paths: 'PATHABLE',
    replace: Optional['REPLACE'] = None,
) -> tuple[Path, ...]:
    """
    Resolve the provided paths replacing the magic keywords.

    .. note::
       This will remove duplicative paths from the returned.

    Example
    -------
    >>> resolve_paths(['/foo/bar'])
    (PosixPath('/foo/bar'),)

    :param paths: Complete or relative paths for processing.
    :param replace: Optional values to replace in the path.
    :returns: New resolved filesystem path object instances.
    """

    returned: list[Path] = []

    if isinstance(paths, str | Path):
        paths = [paths]

    for path in paths:

        resolved = resolve_path(
            path, replace)

        if resolved in returned:
            continue

        returned.append(resolved)

    return tuple(returned)



def stats_path(
    path: str | Path,
    replace: Optional['REPLACE'] = None,
    ignore: Optional[list[str]] = None,
) -> STATS_PATH:
    """
    Collect stats object for the complete or relative path.

    .. testsetup::
       >>> from . import save_text
       >>> path = Path(getfixture('tmpdir'))
       >>> file = path.joinpath('hello.txt')
       >>> save_text(file, 'Hello world!')
       'Hello world!'

    Example
    -------
    >>> replace = {str(path): '/'}
    >>> stats = stats_path(path, replace)
    >>> stats['/hello.txt'].st_size
    12

    :param path: Complete or relative path for enumeration.
    :param replace: Optional values to replace in the path.
    :param ignore: Paths matching these patterns are ignored.
    :returns: Metadata for files recursively found in path.
    """

    path = Path(path).resolve()

    returned: STATS_PATH = {}


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

            stat = item.stat()

            returned[str(key)] = stat


    return sort_dict(returned)
