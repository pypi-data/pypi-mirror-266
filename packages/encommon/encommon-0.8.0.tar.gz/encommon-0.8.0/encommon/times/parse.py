"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from contextlib import suppress
from datetime import datetime
from datetime import timezone
from re import match as re_match
from typing import Optional
from typing import TYPE_CHECKING

from dateutil import parser

from snaptime import snap

from .common import NUMERISH
from .common import PARSABLE
from .common import SNAPABLE
from .common import STRINGNOW
from .common import findtz
from .common import strptime
from .common import utcdatetime

if TYPE_CHECKING:
    from .times import Times  # noqa: F401



def parse_time(  # noqa: CFQ004
    source: Optional[PARSABLE] = None,
    *,
    anchor: Optional[PARSABLE] = None,
    format: Optional[str] = None,
    tzname: Optional[str] = None,
) -> datetime:
    """
    Parse provided time value with various supported formats.

    +----------------------+----------------------------+
    | *Example*            | *Description*              |
    +----------------------+----------------------------+
    | 'now'                | Uses the current time      |
    +----------------------+----------------------------+
    | None, 'None', 'null' | Uses the current time      |
    +----------------------+----------------------------+
    | 'min', float('-inf') | Uses the minimum time      |
    +----------------------+----------------------------+
    | 'max', float('inf')  | Uses the maximum time      |
    +----------------------+----------------------------+
    | object               | Provide datetime or Times  |
    +----------------------+----------------------------+
    | 2000-01-01T00:00:00Z | Uses strptime and dateutil |
    +----------------------+----------------------------+
    | 1645843626.2         | Provide Unix epoch         |
    +----------------------+----------------------------+
    | '-1h@h+5m'           | Provide snaptime syntax    |
    +----------------------+----------------------------+

    Example
    -------
    >>> parse_time('1/1/2000 12:00am')
    datetime.datetime(2000, 1, 1, 0...

    Example
    -------
    >>> parse_time(0)
    datetime.datetime(1970, 1, 1, 0...

    :param source: Time in various forms that will be parsed.
    :param anchor: Optional relative time; for snap notation.
    :param format: Optional format when source is timestamp.
    :param tzname: Name of the timezone associated to source.
        This is not relevant in timezone included in source.
    :returns: Python datetime object containing related time.
    """

    if (source is not None
            and hasattr(source, 'source')):
        source = source.source

    if (isinstance(source, str)
            and re_match(NUMERISH, source)):
        source = float(source)

    tzinfo = findtz(tzname)


    if isinstance(source, (int, float)):
        source = datetime.fromtimestamp(
            float(source), tz=tzinfo)

    if str(source) in STRINGNOW:
        return utcdatetime()

    if source in ['max', float('inf')]:
        source = datetime.max

    if source in ['min', float('-inf')]:
        source = datetime.min

    if (isinstance(source, str)
            and re_match(SNAPABLE, source)):
        return shift_time(
            notate=source,
            anchor=anchor,
            tzname=tzname)

    if isinstance(source, str):
        return string_time(
            source=source,
            formats=format,
            tzname=tzname)

    if isinstance(source, datetime):
        return (
            source.replace(tzinfo=tzinfo)
            .astimezone(timezone.utc))


    raise ValueError('source')  # NOCVR



def shift_time(
    notate: str,
    anchor: Optional[PARSABLE] = None,
    *,
    tzname: Optional[str] = None,
) -> datetime:
    """
    Shift provided time value using snaptime relative syntax.

    Example
    -------
    >>> shift_time('-1h', anchor='1/1/2000 12:00am')
    datetime.datetime(1999, 12, 31, 23...

    Example
    -------
    >>> shift_time('-1h@d', anchor='1/1/2000 12:00am')
    datetime.datetime(1999, 12, 31, 0...

    :param notate: Syntax compatable using snaptime library.
    :param anchor: Optional relative time; for snap notation.
    :param tzname: Name of the timezone associated to anchor.
        This is not relevant in timezone included in anchor.
    :returns: Python datetime object containing related time.
    """

    anchor = parse_time(
        anchor, tzname=tzname)

    return snap(anchor, notate)



def string_time(
    source: str,
    *,
    formats: Optional[str | list[str]] = None,
    tzname: Optional[str] = None,
) -> datetime:
    """
    Parse provided time value with various supported formats.

    Example
    -------
    >>> string_time('2000-01-01T00:00:00Z')
    datetime.datetime(2000, 1, 1, 0...

    Example
    -------
    >>> string_time('2000/01/01')
    datetime.datetime(2000, 1, 1, 0...

    :param source: Time in various forms that will be parsed.
    :param formats: Various formats compatable with strptime.
    :param tzname: Name of the timezone associated to source.
        This is not relevant in timezone included in source.
    :returns: Python datetime object containing related time.
    """

    if formats is not None:
        with suppress(ValueError):
            return strptime(source, formats)

    parsed = parser.parse(source)

    return parse_time(
        parsed, tzname=tzname)



def since_time(
    start: PARSABLE,
    stop: Optional[PARSABLE] = None,
) -> float:
    """
    Determine the time in seconds that occured between values.

    Example
    -------
    >>> start = parse_time(0)
    >>> stop = parse_time(1)
    >>> since_time(start, stop)
    1.0

    :param start: Time in various forms that will be parsed.
    :param stop: Time in various forms that will be parsed.
    :returns: Time in seconds that occured between the values.
    """

    start = parse_time(start)
    stop = parse_time(stop)

    delta = stop - start

    since = delta.total_seconds()

    return abs(since)
