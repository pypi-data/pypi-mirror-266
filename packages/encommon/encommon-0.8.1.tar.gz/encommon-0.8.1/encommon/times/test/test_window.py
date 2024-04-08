"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from typing import TYPE_CHECKING

from pytest import fixture
from pytest import mark

from ..window import Window
from ..window import window_croniter
from ..window import window_interval

if TYPE_CHECKING:
    from ..common import PARSABLE



@fixture
def window() -> Window:
    """
    Construct the instance for use in the downstream tests.

    :returns: Newly constructed instance of related class.
    """

    return Window(
        schedule='* * * * *',
        start=330, stop=630)



def test_Window(
    window: Window,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param window: Primary class instance for window object.
    """


    attrs = list(window.__dict__)

    assert attrs == [
        '_Window__schedule',
        '_Window__start',
        '_Window__stop',
        '_Window__anchor',
        '_Window__delay',
        '_Window__wilast',
        '_Window__winext',
        '_Window__walked']


    assert repr(window)[:22] == (
        '<encommon.times.window')

    assert hash(window) > 0

    assert str(window)[:22] == (
        '<encommon.times.window')


    assert window.schedule == '* * * * *'

    assert window.start == '1970-01-01T00:05:30Z'

    assert window.stop == '1970-01-01T00:10:30Z'

    assert window.anchor == window.start

    assert window.delay == 0.0

    assert window.last == '1970-01-01T00:05:00Z'

    assert window.next == '1970-01-01T00:06:00Z'

    assert window.walked is False



def test_Window_cover(
    window: Window,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param window: Primary class instance for window object.
    """


    window = Window(
        schedule='* * * * *',
        start=window.start,
        stop=window.stop)

    assert window.last == '1970-01-01T00:05:00Z'
    assert window.next == '1970-01-01T00:06:00Z'
    assert window.walked is False

    for count in range(100):
        if window.walk() is False:
            break
        assert window.walk(False)

    assert count == 4
    assert not window.walk()

    assert window.last == '1970-01-01T00:10:00Z'
    assert window.next == '1970-01-01T00:10:00Z'
    assert window.walked is True


    window = Window(
        schedule={'minutes': 1},
        start=window.start,
        stop=window.stop)

    assert window.last == '1970-01-01T00:04:30Z'
    assert window.next == '1970-01-01T00:05:30Z'
    assert window.walked is False

    for count in range(100):
        if window.walk() is False:
            break
        assert window.walk(False)

    assert count == 5
    assert not window.walk()

    assert window.last == '1970-01-01T00:10:30Z'
    assert window.next == '1970-01-01T00:10:30Z'
    assert window.walked is True


    window = Window(
        schedule='* * * * *',
        start='+5m', stop='+10m')

    assert not window.walk(False)



@mark.parametrize(
    'schedule,anchor,backward,expect',
    [('* * * * *', 0, False, (0, 60)),
     ('* * * * *', 1, False, (0, 60)),
     ('* * * * *', 0, True, (-60, 0)),
     ('* * * * *', 1, True, (-60, 0)),
     ('* * * * *', 3559, False, (3540, 3600)),
     ('* * * * *', 3659, False, (3600, 3660)),
     ('* * * * *', 3660, False, (3660, 3720)),
     ('* * * * *', 3661, False, (3660, 3720)),
     ('0 * * * *', 3559, False, (0, 3600)),
     ('0 * * * *', 3660, False, (3600, 7200)),
     ('0 * * * *', 3661, False, (3600, 7200))])
def test_window_croniter(
    schedule: str,
    anchor: 'PARSABLE',
    backward: bool,
    expect: tuple[int, int],
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param schedule: Parameters for defining scheduled time.
    :param anchor: Optionally define time anchor for window.
    :param backward: Optionally operate the window backward.
    :param expect: Expected output from the testing routine.
    """

    window = window_croniter(
        schedule, anchor, backward)

    assert window[0] == expect[0]
    assert window[1] == expect[1]



@mark.parametrize(
    'schedule,anchor,backward,expect',
    [({'seconds': 60}, 0, False, (0, 60)),
     ({'seconds': 60}, 1, False, (1, 61)),
     ({'seconds': 60}, 0, True, (-60, 0)),
     ({'seconds': 60}, 1, True, (-59, 1)),
     ({'seconds': 60}, 3559, False, (3559, 3619)),
     ({'seconds': 60}, 3659, False, (3659, 3719)),
     ({'seconds': 60}, 3660, False, (3660, 3720)),
     ({'seconds': 60}, 3661, False, (3661, 3721)),
     ({'hours': 1}, 3559, False, (3559, 7159)),
     ({'hours': 1}, 3660, False, (3660, 7260)),
     ({'hours': 1}, 3661, False, (3661, 7261))])
def test_window_interval(
    schedule: dict[str, int],
    anchor: 'PARSABLE',
    backward: bool,
    expect: tuple[int, int],
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param schedule: Parameters for defining scheduled time.
    :param anchor: Optionally define time anchor for window.
    :param backward: Optionally operate the window backward.
    :param expect: Expected output from the testing routine.
    """

    window = window_interval(
        schedule, anchor, backward)

    assert window[0] == expect[0]
    assert window[1] == expect[1]
