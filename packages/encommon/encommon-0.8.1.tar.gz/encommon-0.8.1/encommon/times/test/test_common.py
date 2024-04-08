"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from dateutil.tz import gettz

from pytest import raises

from ..common import STAMP_SIMPLE
from ..common import UNIXEPOCH
from ..common import findtz
from ..common import strptime
from ..common import utcdatetime



def test_utcdatetime() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    dtime = utcdatetime(1970, 1, 1)

    assert dtime.year == 1970
    assert dtime.month == 1
    assert dtime.day == 1
    assert dtime.hour == 0
    assert dtime.minute == 0
    assert dtime.second == 0


    dtime = utcdatetime(
        1970, 1, 1,
        tzinfo=gettz('US/Central'))

    assert dtime.year == 1970
    assert dtime.month == 1
    assert dtime.day == 1
    assert dtime.hour == 6
    assert dtime.minute == 0
    assert dtime.second == 0



def test_strptime() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    parsed = strptime(
        UNIXEPOCH, STAMP_SIMPLE)

    assert parsed.year == 1970
    assert parsed.month == 1
    assert parsed.day == 1
    assert parsed.hour == 0
    assert parsed.minute == 0
    assert parsed.second == 0



def test_strptime_raises() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    _raises = raises(ValueError)

    with _raises as reason:
        strptime('foo', '%Y')

    _reason = str(reason.value)

    assert _reason == 'invalid'



def test_findtz() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    tzinfo = findtz('UTC')

    assert 'UTC' in str(tzinfo)



def test_findtz_raises() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    _raises = raises(ValueError)

    with _raises as reason:
        findtz('foo')

    _reason = str(reason.value)

    assert _reason == 'tzname'
