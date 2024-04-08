"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



COMMAS = ', '
COMMAD = ','

NEWLINE = '\n'

SEMPTY = ''
SPACED = ' '



def striplower(
    value: str,
) -> str:
    """
    Return the provided string but stripped and lower cased.

    Example
    -------
    >>> striplower('  Foo ')
    'foo'

    :param value: String which will be stripped and lowered.
    :returns: Provided string but stripped and lower cased.
    """

    return value.strip().lower()
