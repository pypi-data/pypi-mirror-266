"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from datetime import timedelta

from pytest import mark

from ..common import utcdatetime
from ..parse import parse_time
from ..parse import shift_time
from ..parse import since_time
from ..parse import string_time



def test_parse_time() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    dtime = utcdatetime()
    delta = timedelta(seconds=1)


    parsed = parse_time(
        '1/1/1970 6:00am')

    assert parsed.year == 1970
    assert parsed.month == 1
    assert parsed.day == 1
    assert parsed.hour == 6


    parsed = parse_time(
        '12/31/1969 6:00pm',
        tzname='US/Central')

    assert parsed.year == 1970
    assert parsed.month == 1
    assert parsed.day == 1
    assert parsed.hour == 0


    parsed = parse_time(0)
    assert parsed.year == 1970

    parsed = parse_time('0')
    assert parsed.year == 1970


    parsed = parse_time('max')

    assert parsed.year == 9999
    assert parsed.month == 12
    assert parsed.day == 31
    assert parsed.hour == 23

    parsed = parse_time('min')

    assert parsed.year == 1
    assert parsed.month == 1
    assert parsed.day == 1
    assert parsed.hour == 0


    parsed = parse_time('now')
    assert parsed - dtime <= delta

    parsed = parse_time(None)
    assert parsed - dtime <= delta

    parsed = parse_time('None')
    assert parsed - dtime <= delta


    parsed = parse_time('+1y')
    assert parsed - dtime > delta


    _parsed = parse_time(parsed)
    assert _parsed == parsed



@mark.parametrize(
    'notate,expect',
    [('+1y', (1981, 1, 1)),
     ('-1y', (1979, 1, 1)),
     ('+1y@s', (1981, 1, 1)),
     ('-1y@s', (1979, 1, 1)),
     ('+1y@s+1h', (1981, 1, 1, 1)),
     ('-1y@s-1h', (1978, 12, 31, 23)),
     ('+1mon', (1980, 2, 1)),
     ('-1mon', (1979, 12, 1)),
     ('+1mon@m', (1980, 2, 1)),
     ('-1mon@m', (1979, 12, 1)),
     ('+1mon@m+1mon', (1980, 3, 1)),
     ('-1mon@m-1mon', (1979, 11, 1)),
     ('+1w', (1980, 1, 8)),
     ('-1w', (1979, 12, 25)),
     ('+1w@h', (1980, 1, 8)),
     ('-1w@h', (1979, 12, 25)),
     ('+1w@h+1w', (1980, 1, 15)),
     ('-1w@h-1w', (1979, 12, 18)),
     ('+1d', (1980, 1, 2)),
     ('-1d', (1979, 12, 31)),
     ('+1d@d', (1980, 1, 2)),
     ('-1d@d', (1979, 12, 31)),
     ('+1d@d+30d', (1980, 2, 1)),
     ('-1d@d-30d', (1979, 12, 1))])
def test_shift_time(
    notate: str,
    expect: tuple[int, ...],
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param notate: Syntax compatable using snaptime library.
    :param expect: Expected output from the testing routine.
    """

    anchor = utcdatetime(1980, 1, 1)
    dtime = utcdatetime(*expect)

    parsed = shift_time(notate, anchor)

    assert parsed == dtime



def test_string_time() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    expect = utcdatetime(1980, 1, 1)


    strings = [
        '1980-01-01T00:00:00Z',
        '1980-01-01T00:00:00 +0000',
        '1980-01-01T00:00:00',
        '1980-01-01 00:00:00 +0000',
        '1980-01-01 00:00:00']

    for string in strings:

        parsed = string_time(string)

        assert parsed == expect


    parsed = string_time(
        '1980_01_01',
        formats=['%Y_%m_%d'])

    assert parsed == expect


    parsed = string_time(
        '1980_01_01',
        formats='%Y_%m_%d')

    assert parsed == expect


    parsed = string_time(
        '1979-12-31 18:00:00',
        tzname='US/Central')

    assert parsed == expect



def test_since_time() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    parsed = shift_time('-1s')
    since = since_time(parsed)

    assert since >= 1
    assert since < 2


    parsed = shift_time('+1s')
    since = since_time(parsed)

    assert since > 0
    assert since < 2
