"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..duration import Duration
from ...types.strings import COMMAS



def test_Duration() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    durate = Duration(95401)


    attrs = list(durate.__dict__)

    assert attrs == [
        '_Duration__source',
        '_Duration__smart',
        '_Duration__groups']


    assert repr(durate)[:23] == (
        'Duration(seconds=95401.')

    assert hash(durate) > 0

    assert str(durate) == '1d2h30m'


    assert int(durate) == 95401
    assert float(durate) == 95401

    assert durate + 1 == 95402
    assert durate + durate == 190802
    assert durate - 1 == 95400
    assert durate - durate == 0

    assert durate == durate
    assert durate != Duration(60)
    assert durate != 'invalid'

    assert durate > Duration(95400)
    assert durate >= Duration(95401)
    assert durate < Duration(95402)
    assert durate <= Duration(95401)


    assert durate.source == 95401

    assert durate.smart is True

    assert durate.groups == 7

    assert durate.units() == {
        'day': 1,
        'hour': 2,
        'minute': 30}

    assert durate.short == '1d 2h 30m'

    assert durate.compact == '1d2h30m'

    assert durate.verbose == (
        '1 day, 2 hours, 30 minutes')



def test_Duration_cover() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    durate = Duration(
        seconds=7501,
        smart=False)

    assert durate.short == '2h 5m 1s'
    assert durate.compact == '2h5m1s'
    assert durate.verbose == (
        '2 hours, 5 minutes, 1 second')


    durate = Duration(
        groups=3,
        seconds=694800,
        smart=False)

    assert durate.short == '1w 1d 1h'
    assert durate.compact == '1w1d1h'
    assert durate.verbose == (
        '1 week, 1 day, 1 hour')


    durate = Duration(36295261)

    units = durate.units(False)
    assert units == {
        'year': 1, 'week': 3,
        'month': 1, 'day': 4,
        'hour': 2, 'minute': 1}

    units = durate.units(True)
    assert units == {
        'y': 1, 'w': 3, 'mon': 1,
        'd': 4, 'h': 2, 'm': 1}



def test_Duration_iterate() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    second = 60
    hour = second * 60
    day = hour * 24
    week = day * 7
    month = day * 30
    quarter = day * 90
    year = day * 365


    expects = {

        year: (
            '1y', '1 year'),
        year + 1: (
            '1y', '1 year'),
        year - 1: (
            '12mon4d23h59m',
            '12 months, 4 days'),

        quarter: (
            '3mon', '3 months'),
        quarter + 1: (
            '3mon', '3 months'),
        quarter - 1: (
            '2mon4w1d23h59m',
            '2 months, 4 weeks'),

        month: (
            '1mon', '1 month'),
        month + 1: (
            '1mon', '1 month'),
        month - 1: (
            '4w1d23h59m',
            '4 weeks, 1 day'),

        week: (
            '1w', '1 week'),
        week + 1: (
            '1w', '1 week'),
        week - 1: (
            '6d23h59m',
            '6 days, 23 hours'),

        day: (
            '1d', '1 day'),
        day + 1: (
            '1d', '1 day'),
        day - 1: (
            '23h59m',
            '23 hours, 59 minutes'),

        hour: (
            '1h', '1 hour'),
        hour + 1: (
            '1h', '1 hour'),
        hour - 1: (
            '59m', '59 minutes'),

        second: (
            '1m', '1 minute'),
        second + 1: (
            '1m', '1 minute'),
        second - 1: (
            '59s', 'just now')}


    items = expects.items()

    for source, expect in items:

        durate = Duration(source)

        compact, verbose = expect
        _compact = durate.compact
        _verbose = COMMAS.join(
            durate.verbose
            .split(', ')[:2])

        assert _compact == compact
        assert _verbose == verbose
