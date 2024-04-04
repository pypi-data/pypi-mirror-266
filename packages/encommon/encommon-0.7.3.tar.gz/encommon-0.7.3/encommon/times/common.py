"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from contextlib import suppress
from datetime import datetime
from datetime import timezone
from re import compile
from typing import Any
from typing import TYPE_CHECKING
from typing import Union
if TYPE_CHECKING:
    from .times import Times



NUMERISH = compile(r'^\-?\d+(\.\d+)?$')
SNAPABLE = compile(r'^(\-|\+)[\d\@a-z\-\+]+$')
STRINGNOW = {'None', 'null', 'now'}

NUMERIC = Union[int, float]
PARSABLE = Union[str, NUMERIC, datetime, 'Times']
SCHEDULE = Union[str, dict[str, int]]

UNIXEPOCH = '1970-01-01T00:00:00+0000'
UNIXMPOCH = '1970-01-01T00:00:00.000000+0000'
UNIXHPOCH = '01/01/1970 12:00AM UTC'

STAMP_SIMPLE = '%Y-%m-%dT%H:%M:%S%z'
STAMP_SUBSEC = '%Y-%m-%dT%H:%M:%S.%f%z'
STAMP_HUMAN = '%m/%d/%Y %I:%M%p %Z'



def utcdatetime(
    *args: Any,
    **kwargs: Any,
) -> datetime:
    """
    Return the instance of datetime within the UTC timezone.

    .. warning::
       If no arguments are provided, returns current time.

    Example
    -------
    >>> utcdatetime(1970, 1, 1)
    datetime.datetime(1970, 1, 1, 0...

    :param args: Positional arguments passed for downstream.
    :param kwargs: Keyword arguments passed for downstream.
    :returns: Instance of datetime within the UTC timezone.
    """

    if not args and not kwargs:
        return datetime.now(tz=timezone.utc)

    if 'tzinfo' not in kwargs:
        kwargs['tzinfo'] = timezone.utc

    return (
        datetime(*args, **kwargs)  # noqa: DTZ001
        .astimezone(timezone.utc))



def strptime(
    source: str,
    formats: str | list[str],
) -> datetime:
    """
    Parse provided time value with various supported formats.

    Example
    -------
    >>> strptime('2023', '%Y')
    datetime.datetime(2023, 1, 1, 0...

    :param source: Time in various forms that will be parsed.
    :param formats: Various formats compatable with strptime.
    :returns: Python datetime object containing related time.
    """

    if isinstance(formats, str):
        formats = [formats]


    def _strptime(
        format: str,
    ) -> datetime:
        return (
            datetime
            .strptime(source, format)
            .astimezone(timezone.utc))


    for format in formats:
        with suppress(ValueError):
            return _strptime(format)

    raise ValueError('invalid')
