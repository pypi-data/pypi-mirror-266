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
from typing import TYPE_CHECKING

from . import read_text
from . import save_text

if TYPE_CHECKING:
    from .common import REPLACE



def prep_sample(
    content: Any,
    *,
    default: Callable[[Any], str] = str,
    replace: Optional['REPLACE'] = None,
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

    :param content: Content that will be processed as JSON.
    :param default: Callable used when stringifying values.
    :param replace: Optional values to replace in the file.
    :returns: Content after processing using JSON functions.
    """

    content = dumps(
        content, default=default)

    prefix = 'encommon_sample'

    replace = replace or {}

    items = replace.items()

    for old, new in items:

        if isinstance(old, Path):
            old = str(old)

        if isinstance(new, Path):
            new = str(new)

        content = content.replace(
            new, f'_/{prefix}/{old}/_')

    return loads(content)



def load_sample(
    path: str | Path,
    content: Optional[Any] = None,
    update: bool = False,
    *,
    default: Callable[[Any], str] = str,
    replace: Optional['REPLACE'] = None,
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

    :param path: Complete or relative path for the sample.
    :param update: Determine whether the sample is updated.
    :param content: Content that will be processed as JSON.
    :param default: Callable used when stringifying values.
    :param replace: Optional values to replace in the file.
    :returns: Content after processing using JSON functions.
    """

    path = Path(path).resolve()

    loaded: Optional[Any] = None


    content = prep_sample(
        content=content,
        default=default,
        replace=replace)


    def _save_sample() -> None:

        dumped = dumps(
            content, indent=2)

        save_text(path, dumped)


    def _load_sample() -> Any:

        loaded = read_text(path)

        return loads(loaded)


    if path.exists():
        loaded = _load_sample()

    if not path.exists():
        _save_sample()

    elif (update is True
            and content is not None
            and content != loaded):
        _save_sample()


    return _load_sample()
