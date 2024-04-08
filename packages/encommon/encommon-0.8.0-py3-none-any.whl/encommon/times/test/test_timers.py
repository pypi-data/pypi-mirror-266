"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from time import sleep

from pytest import fixture
from pytest import raises

from ..timers import Timers



@fixture
def timers(
    tmp_path: Path,
) -> Timers:
    """
    Construct the instance for use in the downstream tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: Newly constructed instance of related class.
    """

    return Timers(
        timers={'one': 1},
        file=f'{tmp_path}/cache.db')



def test_Timers(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """


    attrs = list(timers.__dict__)

    assert attrs == [
        '_Timers__config',
        '_Timers__sqlite',
        '_Timers__file',
        '_Timers__table',
        '_Timers__cache']


    assert repr(timers)[:22] == (
        '<encommon.times.timers')

    assert hash(timers) > 0

    assert str(timers)[:22] == (
        '<encommon.times.timers')


    assert timers.timers == {'one': 1}

    assert timers.sqlite is not None

    assert timers.file[-8:] == 'cache.db'

    assert timers.table == 'timers'

    assert list(timers.cache) == ['one']



def test_Timers_cover(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """


    assert not timers.ready('one')

    sleep(1.1)

    assert timers.ready('one')


    timers.create('two', 2, 0)

    assert timers.ready('two')

    assert not timers.ready('two')



def test_Timers_cache(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """

    timers1 = Timers(
        timers={'uno': 1},
        file=timers.file)

    assert not timers1.ready('uno')

    sleep(0.75)

    timers2 = Timers(
        timers={'uno': 1},
        file=timers.file)

    assert not timers1.ready('uno')
    assert not timers2.ready('uno')

    sleep(0.25)

    timers2.load_cache()

    assert timers1.ready('uno')
    assert timers2.ready('uno')



def test_Timers_raises(
    timers: Timers,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param timers: Primary class instance for timers object.
    """


    _raises = raises(ValueError)

    with _raises as reason:
        timers.ready('dne')

    _reason = str(reason.value)

    assert _reason == 'unique'


    _raises = raises(ValueError)

    with _raises as reason:
        timers.update('dne')

    _reason = str(reason.value)

    assert _reason == 'unique'


    _raises = raises(ValueError)

    with _raises as reason:
        timers.create('one', 1)

    _reason = str(reason.value)

    assert _reason == 'unique'
