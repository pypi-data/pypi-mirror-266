"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from json import dumps
from json import loads
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional

from .. import PROJECT
from .. import WORKSPACE



def prep_sample(
    content: Any,
    *,
    default: Callable[[Any], str] = str,
    replace: Optional[dict[str, str | Path]] = None,
) -> Any:
    """
    Return the content after processing using JSON functions.

    .. testsetup::
       >>> from ..types import Empty

    Example
    -------
    >>> prep_sample(['one', 'two'])
    ['one', 'two']

    Example
    -------
    >>> prep_sample({'one': Empty})
    {'one': 'Empty'}

    :param content: Content which will be processed for JSON.
    :param default: Callable used when stringifying values.
    :param replace: Optional string values to replace in path.
    :returns: Content after processing using JSON functions.
    """

    content = dumps(
        content, default=default)

    prefix = 'encommon_sample'

    replace = replace or {}

    replace |= {
        'PROJECT': PROJECT,
        'WORKSPACE': WORKSPACE}

    for old, new in replace.items():

        if isinstance(new, Path):
            new = str(new)

        content = content.replace(
            new, f'_/{prefix}/{old}/_')

    return loads(content)



def load_sample(
    path: Path,
    content: Optional[Any] = None,
    update: bool = False,
    *,
    default: Callable[[Any], str] = str,
    replace: Optional[dict[str, str | Path]] = None,
) -> Any:
    """
    Load the sample file and compare using provided content.

    .. testsetup::
       >>> from json import dumps
       >>> from json import loads
       >>> path = Path(getfixture('tmpdir'))
       >>> sample = path.joinpath('sample')

    Example
    -------
    >>> content = {'one': 'two'}
    >>> load_sample(sample, content)
    {'one': 'two'}

    Example
    -------
    >>> load_sample(sample)
    {'one': 'two'}

    :param path: Complete or relative path to the sample file.
    :param update: Determine whether the sample is updated.
    :param content: Content which will be processed for JSON.
    :param default: Callable used when stringifying values.
    :param replace: Optional string values to replace in file.
    :returns: Content after processing using JSON functions.
    """

    loaded: Optional[Any] = None

    content = prep_sample(
        content=content,
        default=default,
        replace=replace)


    def _save_sample() -> None:
        path.write_text(
            dumps(content, indent=2))


    def _load_sample() -> Any:
        return loads(
            path.read_text(
                encoding='utf-8'))


    if path.exists():
        loaded = _load_sample()

    if not path.exists():
        _save_sample()

    elif (update is True
            and content is not None
            and content != loaded):
        _save_sample()


    return _load_sample()
