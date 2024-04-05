"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from dateutil.tz import gettz

from pytest import raises

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


    dtime = utcdatetime(
        1970, 1, 1,
        tzinfo=gettz('US/Central'))

    assert dtime.year == 1970
    assert dtime.month == 1
    assert dtime.day == 1
    assert dtime.hour == 6


    assert utcdatetime().year >= 2023



def test_strptime() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    dtime = strptime('1970', '%Y')

    assert dtime.year == 1970
    assert dtime.month == 1
    assert dtime.day == 1
    assert dtime.hour == 0


    dtime = strptime('1970', ['%Y'])

    assert dtime.year == 1970
    assert dtime.month == 1
    assert dtime.day == 1
    assert dtime.hour == 0



def test_strptime_raises() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    with raises(ValueError) as reason:
        strptime('foo', '%Y')

    assert str(reason.value) == 'invalid'
