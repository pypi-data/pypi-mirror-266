"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from fnmatch import fnmatch
from re import fullmatch as re_fmatch
from re import match as re_match



def rgxp_match(
    values: str | list[str],
    patterns: str | list[str],
    complete: bool = False,
) -> bool:
    """
    Determine whether or not values are included by patterns.

    Example
    -------
    >>> rgxp_match('one', ['on*', 'two'])
    True

    Example
    -------
    >>> rgxp_match('uno', ['on*', 'two'])
    False

    :param values: Value or values to enumerate for matching.
    :param patterns: Patterns which values can match any one.
    :param complete: Whether or not whole string must match.
    :returns: Boolean indicating outcome from the operation.
    """

    if isinstance(values, str):
        values = [values]

    if isinstance(patterns, str):
        patterns = [patterns]

    outcomes: set[bool] = set()

    function = (
        re_fmatch if complete
        else re_match)


    def _matches() -> bool:

        return bool(
            function(pattern, value))


    for value in values:

        matched = False

        for pattern in patterns:

            if not _matches():
                continue

            matched = True

            break

        outcomes.add(matched)


    return bool(
        outcomes and all(outcomes))



def fuzz_match(
    values: str | list[str],
    patterns: str | list[str],
) -> bool:
    """
    Determine whether or not values are included by patterns.

    Example
    -------
    >>> rgxp_match('one', ['on[a-z]', 'two'])
    True

    Example
    -------
    >>> rgxp_match('uno', ['on[a-z]', 'two'])
    False

    :param values: Value or values to enumerate for matching.
    :param patterns: Patterns which values can match any one.
    :returns: Boolean indicating outcome from the operation.
    """

    if isinstance(values, str):
        values = [values]

    if isinstance(patterns, str):
        patterns = [patterns]

    outcomes: set[bool] = set()


    for value in values:

        matched = False

        for pattern in patterns:

            if not fnmatch(value, pattern):
                continue

            matched = True

            break

        outcomes.add(matched)


    return bool(
        outcomes and all(outcomes))
