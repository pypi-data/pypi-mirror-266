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



CACHE_TABLE = (
    """
    create table if not exists
     {0} (
      "unique" text not null,
      "update" text not null,
     primary key ("unique"));
    """)  # noqa: LIT003



_TIMERS = dict[str, float]
_CACHED = dict[str, Times]



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
    :param file: Optional path to SQLite database for
        cache. This will allow for use between executions.
    :param table: Optional override default table name.
    """

    __config: _TIMERS
    __sqlite: 'Connection'
    __file: str
    __table: str
    __cache: _CACHED


    def __init__(
        self,
        timers: Optional[dict[str, NUMERIC]] = None,
        file: str = ':memory:',
        table: str = 'timers',
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """


        timers = dict(timers or {})

        items = timers.items()

        for key, value in items:
            timers[key] = float(value)


        sqlite = SQLite(file)

        sqlite.execute(
            CACHE_TABLE
            .format(table))

        sqlite.commit()


        cached: _CACHED = {}

        for timer in timers:
            cached[timer] = Times()


        self.__config = timers
        self.__sqlite = sqlite
        self.__file = file
        self.__table = table
        self.__cache = cached


        self.load_cache()
        self.save_cache()


    def load_cache(
        self,
    ) -> None:
        """
        Load the timers cache from the database into attribute.
        """

        cached = self.__sqlite
        table = self.__table
        cachem = self.__cache

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

        insert = tuple[str, str]
        inserts: list[insert] = []


        cached = self.__sqlite
        table = self.__table
        cachem = self.__cache


        items = cachem.items()

        for key, value in items:

            append = (key, str(value))

            inserts.append(append)


        cached.executemany(
            (f'replace into {table}'
             ' ("unique", "update")'
             ' values (?, ?)'),
            tuple(sorted(inserts)))

        cached.commit()


    @property
    def timers(
        self,
    ) -> _TIMERS:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return dict(self.__config)


    @property
    def sqlite(
        self,
    ) -> 'Connection':
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__sqlite


    @property
    def file(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__file


    @property
    def table(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__table


    @property
    def cache(
        self,
    ) -> _CACHED:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return dict(self.__cache)


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

        :param unique: Which timer configuration from reference.
        :param update: Determines whether or not time is updated.
        """

        config = self.__config
        caches = self.__cache

        if unique not in caches:
            raise ValueError('unique')

        cache = caches[unique]
        timer = config[unique]

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

        :param unique: Which timer configuration from reference.
        :param started: Override the start time for timer value.
        """

        caches = self.__cache

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

        :param unique: Which timer configuration from reference.
        :param minimum: Determine minimum seconds that must pass.
        :param started: Determine when time starts for the timer.
        """

        config = self.__config
        caches = self.__cache

        if unique in config:
            raise ValueError('unique')

        config[unique] = float(minimum)
        caches[unique] = Times(started)

        self.save_cache()
