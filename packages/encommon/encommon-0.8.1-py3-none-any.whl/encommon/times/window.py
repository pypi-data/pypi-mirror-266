"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import copy
from datetime import datetime
from datetime import timedelta
from typing import Optional

from croniter import croniter

from .common import NUMERIC
from .common import PARSABLE
from .common import SCHEDULE
from .parse import parse_time
from .times import Times



class Window:
    """
    Process and operate crontab or interval based schedule.

    .. testsetup::
       >>> from time import sleep

    Example
    -------
    >>> window = Window('* * * * *', '-4m@m')
    >>> [window.walk() for _ in range(6)]
    [True, True, True, True, True, False]

    :param schedule: Parameters for defining scheduled time.
    :param start: Determine the start for scheduling window.
    :param stop: Determine the ending for scheduling window.
    :param anchor: Optionally define time anchor for window.
    :param delay: Period of time schedulng will be delayed.
    """

    __schedule: SCHEDULE
    __start: Times
    __stop: Times
    __anchor: Times
    __delay: float

    __wilast: Times
    __winext: Times
    __walked: bool


    def __init__(
        self,
        schedule: SCHEDULE,
        start: PARSABLE = 'now',
        stop: PARSABLE = '3000-01-01',
        anchor: Optional[PARSABLE] = None,
        delay: NUMERIC = 0,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        if anchor is None:
            anchor = start

        schedule = copy(schedule)
        start = Times(start)
        stop = Times(stop)
        anchor = Times(anchor)
        delay = float(delay)

        assert stop > start


        self.__schedule = schedule
        self.__start = start
        self.__stop = stop
        self.__anchor = anchor
        self.__delay = delay


        wilast, winext = (
            self.__wifunc(anchor))

        while winext > start:
            wilast, winext = (
                self.__wifunc(wilast, True))

        while winext < start:
            wilast, winext = (
                self.__wifunc(winext, False))

        self.__wilast = wilast
        self.__winext = winext


        latest = stop - delay

        self.__walked = winext > latest


    @property
    def schedule(
        self,
    ) -> SCHEDULE:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return copy(self.__schedule)


    @property
    def start(
        self,
    ) -> Times:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Times(self.__start)


    @property
    def stop(
        self,
    ) -> Times:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Times(self.__stop)


    @property
    def anchor(
        self,
    ) -> Times:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Times(self.__anchor)


    @property
    def delay(
        self,
    ) -> float:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__delay


    @property
    def last(
        self,
    ) -> Times:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Times(self.__wilast)


    @property
    def next(
        self,
    ) -> Times:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Times(self.__winext)


    @property
    def walked(
        self,
    ) -> bool:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__walked


    def __wifunc(
        self,
        anchor: PARSABLE,
        backward: bool = False,
    ) -> tuple[Times, Times]:
        """
        Determine next and last windows for window using anchor.

        :param anchor: Optionally define time anchor for window.
        :param backward: Optionally operate the window backward.
        :returns: Next and previous windows for schedule window.
        """

        if isinstance(self.__schedule, str):
            return window_croniter(
                self.__schedule,
                anchor, backward)

        if isinstance(self.__schedule, dict):
            return window_interval(
                self.__schedule,
                anchor, backward)


    def walk(  # noqa: CFQ004
        self,
        update: bool = True,
    ) -> bool:
        """
        Walk the internal time using current position in schedule.

        :param update: Update internal scheduling for operation.
        :returns: Boolean indicating outcome from the operation.
        """

        stop = self.__stop
        delay = self.__delay
        winext = self.__winext
        walked = self.__walked

        if walked is True:
            return False


        _wilast, _winext = (
            self.__wifunc(winext))

        soonest = Times() - delay
        latest = stop - delay


        if update is False:

            if _winext > latest:
                return not walked

            if winext < soonest:
                return True


        elif _winext > latest:
            self.__wilast = _wilast
            self.__walked = True
            return False

        elif self.__winext < soonest:
            self.__wilast = _wilast
            self.__winext = _winext
            return True


        return False



def window_croniter(  # noqa: CFQ004
    schedule: str,
    anchor: PARSABLE,
    backward: bool = False,
) -> tuple[Times, Times]:
    """
    Determine next and previous windows for cronjob schedule.

    :param schedule: Parameters for defining scheduled time.
    :param anchor: Optionally define time anchor for window.
    :param backward: Optionally operate the window backward.
    :returns: Next and previous windows for schedule window.
    """

    anchor = parse_time(anchor)


    def _winext(
        source: datetime,
    ) -> datetime:
        return parse_time(
            _operator(source)
            .get_next())


    def _wilast(
        source: datetime,
    ) -> datetime:
        return parse_time(
            _operator(source)
            .get_prev())


    def _operator(
        source: datetime,
    ) -> croniter:
        return croniter(schedule, source)


    winext = _winext(anchor)

    if backward is True:
        winext = _wilast(winext)

    wilast = _wilast(winext)


    return (Times(wilast), Times(winext))



def window_interval(
    schedule: dict[str, int],
    anchor: PARSABLE,
    backward: bool = False,
) -> tuple[Times, Times]:
    """
    Determine next and previous windows for interval schedule.

    :param schedule: Parameters for defining scheduled time.
    :param anchor: Optionally define time anchor for window.
    :param backward: Optionally operate the window backward.
    :returns: Next and previous windows for schedule window.
    """

    anpoch = (
        parse_time(anchor)
        .timestamp())

    seconds = (
        timedelta(**schedule)
        .seconds)


    if backward is True:
        winext = anpoch
        wilast = anpoch - seconds
    else:
        winext = anpoch + seconds
        wilast = anpoch


    return (Times(wilast), Times(winext))
