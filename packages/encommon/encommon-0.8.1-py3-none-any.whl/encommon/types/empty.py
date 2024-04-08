"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from typing import Optional



class EmptyType:
    """
    Useful for representing empty or absent value with typing.

    .. testsetup::
       >>> from copy import deepcopy

    Example
    -------
    >>> 'foo' if Empty else 'bar'
    'bar'

    Example
    -------
    >>> deepcopy(Empty) is Empty
    True
    """

    __empty: Optional['EmptyType'] = None


    def __init__(
        self,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.__empty = None


    def __new__(
        cls,
    ) -> 'EmptyType':
        """
        Built-in method called when creating new class instance.

        :returns: Same instance of class that first instantiated.
        """

        empty = cls.__empty

        if empty is not None:
            return empty

        cls.__empty = (
            object.__new__(cls))

        return cls.__empty


    def __repr__(
        self,
    ) -> str:
        """
        Built-in method for representing the values for instance.

        :returns: String representation for values from instance.
        """

        return 'Empty'


    def __hash__(
        self,
    ) -> int:
        """
        Built-in method called when performing hashing operation.

        :returns: Boolean indicating outcome from the operation.
        """

        return hash(EmptyType)


    def __str__(
        self,
    ) -> str:
        """
        Built-in method for representing the values for instance.

        :returns: String representation for values from instance.
        """

        return 'Empty'


    def __bool__(
        self,
    ) -> bool:
        """
        Built-in method representing boolean value for instance.

        :returns: Boolean indicating outcome from the operation.
        """

        return False


    def __eq__(
        self,
        other: object,
    ) -> bool:
        """
        Built-in method for comparing this instance with another.

        :param other: Other value being compared with instance.
        :returns: Boolean indicating outcome from the operation.
        """

        return isinstance(other, type(self))


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



Empty = EmptyType()
