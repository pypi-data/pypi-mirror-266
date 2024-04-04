"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..duration import Duration



def test_Duration() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    duration = Duration(95401)

    attrs = list(duration.__dict__)

    assert attrs == [
        '_Duration__source',
        '_Duration__smart',
        '_Duration__groups']


    assert repr(duration) == (
        'Duration('
        'seconds=95401.0, '
        'smart=True, '
        'groups=7)')

    assert isinstance(hash(duration), int)
    assert str(duration) == '1d2h30m'


    assert int(duration) == 95401
    assert float(duration) == 95401

    assert duration + 1 == 95402
    assert duration + duration == 190802
    assert duration - 1 == 95400
    assert duration - duration == 0

    assert duration == duration
    assert duration != Duration(60)
    assert duration != 'invalid'

    assert duration > Duration(95400)
    assert duration >= Duration(95401)
    assert duration < Duration(95402)
    assert duration <= Duration(95401)


    assert duration.source == 95401
    assert duration.smart is True
    assert duration.groups == 7

    assert duration.short == '1d 2h 30m'
    assert duration.compact == '1d2h30m'
    assert duration.verbose == (
        '1 day, 2 hours, 30 minutes')

    assert duration.units() == {
        'day': 1,
        'hour': 2,
        'minute': 30}


    duration = Duration(
        seconds=7501,
        smart=False)

    assert duration.short == '2h 5m 1s'
    assert duration.compact == '2h5m1s'
    assert duration.verbose == (
        '2 hours, 5 minutes, 1 second')


    duration = Duration(
        seconds=694800,
        smart=False,
        groups=3)

    assert duration.short == '1w 1d 1h'
    assert duration.compact == '1w1d1h'
    assert duration.verbose == (
        '1 week, 1 day, 1 hour')


    duration = Duration(36295261)

    assert duration.units() == {
        'year': 1,
        'week': 3,
        'month': 1,
        'day': 4,
        'hour': 2,
        'minute': 1}

    assert duration.units(True) == {
        'y': 1,
        'w': 3,
        'mon': 1,
        'd': 4,
        'h': 2,
        'm': 1}



def test_Duration_cover() -> None:
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

        year: ('1y', '1 year'),
        year + 1: ('1y', '1 year'),
        year - 1: (
            '12mon4d23h59m',
            '12 months, 4 days'),

        quarter: ('3mon', '3 months'),
        quarter + 1: ('3mon', '3 months'),
        quarter - 1: (
            '2mon4w1d23h59m',
            '2 months, 4 weeks'),

        month: ('1mon', '1 month'),
        month + 1: ('1mon', '1 month'),
        month - 1: (
            '4w1d23h59m',
            '4 weeks, 1 day'),

        week: ('1w', '1 week'),
        week + 1: ('1w', '1 week'),
        week - 1: (
            '6d23h59m',
            '6 days, 23 hours'),

        day: ('1d', '1 day'),
        day + 1: ('1d', '1 day'),
        day - 1: (
            '23h59m',
            '23 hours, 59 minutes'),

        hour: ('1h', '1 hour'),
        hour + 1: ('1h', '1 hour'),
        hour - 1: ('59m', '59 minutes'),

        second: ('1m', '1 minute'),
        second + 1: ('1m', '1 minute'),
        second - 1: ('59s', 'just now')}


    for source, expect in expects.items():

        duration = Duration(source)
        assert duration.compact == expect[0]

        duration = Duration(source)
        verbose = ', '.join(
            duration.verbose.split(', ')[:2])

        assert verbose == expect[1]
