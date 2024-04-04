"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from typing import Literal
from typing import Union
from typing import get_args



DURAGROUP = Literal[
    'year', 'month', 'week',
    'day', 'hour', 'minute',
    'second']

DURASHORT = Literal[
    'y', 'mon', 'w',
    'd', 'h', 'm', 's']

DURAMAPS = dict(zip(
    get_args(DURAGROUP),
    get_args(DURASHORT)))

DURAUNITS = Union[
    DURAGROUP, DURASHORT]



class Duration:
    """
    Convert provided the seconds into a human friendly format.

    Example
    -------
    >>> Duration(86400 * 700).compact
    '1y11mon5d'

    Example
    -------
    >>> Duration(86400 * 700).verbose
    '1 year, 11 months, 5 days'

    Example
    -------
    >>> Duration(7201, False).verbose
    '2 hours, 1 second'

    :param seconds: Period in seconds that will be iterated.
    :param smart: Determines if we hide seconds after minute.
    :param groups: Determine the amount of groups to show,
        ensuring the larger units are returned before smaller.
    """

    __source: float
    __smart: bool
    __groups: int


    def __init__(
        self,
        seconds: int | float,
        smart: bool = True,
        groups: int = len(DURAMAPS),
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.__source = float(seconds)
        self.__smart = bool(smart)
        self.__groups = int(groups)


    def __repr__(
        self,
    ) -> str:
        """
        Built-in method for representing the values for instance.

        :returns: String representation for values from instance.
        """

        return (
            f'Duration('
            f'seconds={self.source}, '
            f'smart={self.smart}, '
            f'groups={self.groups})')


    def __hash__(
        self,
    ) -> int:
        """
        Built-in method called when performing hashing operation.

        :returns: Boolean indicating outcome from the operation.
        """

        return int(self.__source * 100000)


    def __str__(
        self,
    ) -> str:
        """
        Built-in method for representing the values for instance.

        :returns: String representation for values from instance.
        """

        return self.compact


    def __int__(
        self,
    ) -> int:
        """
        Built-in method representing numeric value for instance.

        :returns: Numeric representation for values from instance.
        """

        return int(self.__source)


    def __float__(
        self,
    ) -> float:
        """
        Built-in method representing numeric value for instance.

        :returns: Numeric representation for values from instance.
        """

        return float(self.__source)


    def __add__(
        self,
        other: Union['Duration', int, float],
    ) -> float:
        """
        Built-in method for mathematically processing the value.

        :param other: Other value being compared with instance.
        :returns: Python timedelta object containing the answer.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source + other


    def __sub__(
        self,
        other: Union['Duration', int, float],
    ) -> float:
        """
        Built-in method for mathematically processing the value.

        :param other: Other value being compared with instance.
        :returns: Python timedelta object containing the answer.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source - other


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source == other


    def __ne__(
        self,
        other: object,
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        return not self.__eq__(other)


    def __gt__(
        self,
        other: Union['Duration', int, float],
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source > other


    def __ge__(
        self,
        other: Union['Duration', int, float],
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source >= other


    def __lt__(
        self,
        other: Union['Duration', int, float],
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source < other


    def __le__(
        self,
        other: Union['Duration', int, float],
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        if hasattr(other, 'source'):
            other = other.source

        return self.__source <= other


    @property
    def source(
        self,
    ) -> float:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__source


    @property
    def smart(
        self,
    ) -> bool:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__smart


    @property
    def groups(
        self,
    ) -> int:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__groups


    def units(
        self,
        short: bool = False,
    ) -> dict[DURAUNITS, int]:
        """
        Return the groups of time units with each relevant value.

        :param short: Determine if we should use the short hand.
        :returns: Groups of time units with each relevant value.
        """

        source = self.__source
        seconds = int(source)

        returned: dict[DURAUNITS, int] = {}

        groups: dict[DURAGROUP, int] = {
            'year': 31536000,
            'month': 2592000,
            'week': 604800,
            'day': 86400,
            'hour': 3600,
            'minute': 60}


        for key, value in groups.items():

            if seconds < value:
                continue

            _value = seconds // value

            returned[key] = _value

            seconds %= value


        if (source < 60
                or (seconds >= 1
                    and source > 60)):
            returned['second'] = seconds

        if (self.__smart
                and 'second' in returned
                and len(returned) >= 2):
            del returned['second']


        items = (
            list(returned.items())
            [:self.__groups])

        if short is False:
            return dict(items)

        return {
            DURAMAPS[k]: v
            for k, v in items}


    def __duration(
        self,
        delim: str = ' ',
        short: bool = True,
    ) -> str:
        """
        Return the compact format calculated from source duration.

        :param delim: Optional delimiter for between the groups.
        :param short: Determine if we should use the short hand.
        :returns: Compact format calculated from source duration.
        """

        parts: list[str] = []

        groups = self.units(short)
        spaced = '' if short else ' '

        for part, value in groups.items():

            unit: str = part

            if (short is False
                    and value != 1):
                unit += 's'

            parts.append(
                f'{value}{spaced}{unit}')

        return delim.join(parts)


    @property
    def short(
        self,
    ) -> str:
        """
        Return the compact format calculated from source duration.

        :returns: Compact format calculated from source duration.
        """

        return self.__duration()


    @property
    def compact(
        self,
    ) -> str:
        """
        Return the compact format calculated from source duration.

        :returns: Compact format calculated from source duration.
        """

        return self.short.replace(' ', '')


    @property
    def verbose(
        self,
    ) -> str:
        """
        Return the verbose format calculated from source duration.

        :returns: Compact format calculated from source duration.
        """

        if self.__source < 60:
            return 'just now'

        return self.__duration(', ', False)
