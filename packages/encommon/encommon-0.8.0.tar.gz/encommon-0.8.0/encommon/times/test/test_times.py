"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..common import STAMP_SIMPLE
from ..common import UNIXEPOCH
from ..common import UNIXHPOCH
from ..common import UNIXMPOCH
from ..times import Times



def test_Times() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    times = Times(
        UNIXEPOCH,
        format=STAMP_SIMPLE)


    attrs = list(times.__dict__)

    assert attrs == [
        '_Times__source',
        '_Times__hashed']


    assert repr(times)[:23] == (
        "Times('1970-01-01T00:00")

    assert hash(times) > 0

    assert str(times)[:23] == (
        '1970-01-01T00:00:00.000')


    assert int(times) == 0
    assert float(times) == 0.0

    assert times + 1 == Times(1)
    assert times - 1 == Times(-1)

    assert times == Times(0)
    assert times != Times(-1)
    assert times != 'invalid'

    assert times > Times(-1)
    assert times >= Times(0)
    assert times < Times(1)
    assert times <= Times(0)


    assert times.source.year == 1970

    assert times.epoch == 0.0

    assert times.mpoch == 0.0

    assert times.simple == UNIXEPOCH

    assert times.subsec == UNIXMPOCH

    assert times.human == UNIXHPOCH

    assert times.elapsed >= 1672531200

    assert times.since >= 1672531200

    assert times.before == (
        '1969-12-31T23:59:59.999999Z')

    assert times.after == (
        '1970-01-01T00:00:00.000001Z')

    assert times.stamp() == UNIXMPOCH

    times = times.shift('+1y')
    assert times == '1971-01-01'
