"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from sqlite3 import connect as SQLite
from typing import Optional
from typing import TYPE_CHECKING

from .common import NUMERIC
from .common import PARSABLE
from .times import Times

if TYPE_CHECKING:
    from sqlite3 import Connection



TABLE = (
    """
    create table
     if not exists
     {0} (
      "unique" text not null,
      "update" text not null,
     primary key ("unique"));
    """)  # noqa: LIT003



class Timers:
    """
    Track timers on unique key and determine when to proceed.

    .. warning::
       This class will use an in-memory database for cache,
       unless a cache file is explicity defined.

    .. testsetup::
       >>> from time import sleep

    Example
    -------
    >>> timers = Timers({'one': 1})
    >>> timers.ready('one')
    False
    >>> sleep(1)
    >>> timers.ready('one')
    True

    :param timers: Seconds that are used for each of timers.
    :param cache_file: Optional path to SQLite database for
        cache. This will allow for use between executions.
    :param cache_name: Optional override default table name.
    """

    __timers: dict[str, float]
    __cache_file: 'Connection'
    __cache_name: str
    __cache_dict: dict[str, Times]


    def __init__(
        self,
        timers: Optional[dict[str, NUMERIC]] = None,
        cache_file: str = ':memory:',
        cache_name: str = 'encommon_timers',
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        timers = timers or {}


        self.__timers = {
            k: float(v)
            for k, v in
            timers.items()}


        cached = SQLite(cache_file)

        cached.execute(
            TABLE.format(cache_name))

        cached.commit()

        self.__cache_file = cached
        self.__cache_name = cache_name


        self.__cache_dict = {
            x: Times()
            for x in
            self.__timers}


        self.load_cache()
        self.save_cache()


    def load_cache(
        self,
    ) -> None:
        """
        Load the timers cache from the database into attribute.
        """

        cached = self.__cache_file
        table = self.__cache_name
        cachem = self.__cache_dict

        cursor = cached.execute(
            f'select * from {table}'
            ' order by "unique" asc')

        records = cursor.fetchall()

        for record in records:

            unique = record[0]
            update = record[1]

            times = Times(update)

            cachem[unique] = times


    def save_cache(
        self,
    ) -> None:
        """
        Save the timers cache from the attribute into database.
        """

        cached = self.__cache_file
        table = self.__cache_name
        cachem = self.__cache_dict

        insert = [
            (k, str(v)) for k, v
            in cachem.items()]

        cached.executemany(
            (f'replace into {table}'
             ' ("unique", "update")'
             ' values (?, ?)'),
            tuple(insert))

        cached.commit()


    @property
    def timers(
        self,
    ) -> dict[str, float]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return dict(self.__timers)


    @property
    def cache_file(
        self,
    ) -> 'Connection':
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__cache_file


    @property
    def cache_dict(
        self,
    ) -> dict[str, Times]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return dict(self.__cache_dict)


    @property
    def cache_name(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__cache_name


    def ready(
        self,
        unique: str,
        update: bool = True,
    ) -> bool:
        """
        Determine whether or not the appropriate time has passed.

        .. note::
           For performance reasons, this method will not notice
           changes within the database unless refreshed first.

        :param unique: Unique identifier for the timer in mapping.
        :param update: Determines whether or not time is updated.
        """

        timers = self.__timers
        caches = self.__cache_dict

        if unique not in caches:
            raise ValueError('unique')

        cache = caches[unique]
        timer = timers[unique]

        ready = cache.since >= timer

        if ready and update:
            self.update(unique)

        return ready


    def update(
        self,
        unique: str,
        started: Optional[PARSABLE] = None,
    ) -> None:
        """
        Update the existing timer from mapping within the cache.

        :param unique: Unique identifier for the timer in mapping.
        :param started: Override the start time for timer value.
        """

        caches = self.__cache_dict

        if unique not in caches:
            raise ValueError('unique')

        caches[unique] = Times(started)

        self.save_cache()


    def create(
        self,
        unique: str,
        minimum: int | float,
        started: Optional[PARSABLE] = None,
    ) -> None:
        """
        Update the existing timer from mapping within the cache.

        :param unique: Unique identifier for the timer in mapping.
        :param minimum: Determines minimum seconds that must pass.
        :param started: Determines when the time starts for timer.
        """

        timers = self.__timers
        caches = self.__cache_dict

        if unique in timers:
            raise ValueError('unique')

        timers[unique] = float(minimum)
        caches[unique] = Times(started)

        self.save_cache()
