"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from typing import Any



def merge_dicts(
    dict1: dict[Any, Any],
    dict2: dict[Any, Any],
    force: bool = False,
    *,
    merge_list: bool = True,
    merge_dict: bool = True,
) -> None:
    """
    Recursively merge the contents of provided dictionaries.

    .. warning::
       This function will update the ``dict1`` reference.

    Example
    -------
    >>> dict1 = {'a': 'b', 'c': [1]}
    >>> dict2 = {'a': 'B', 'c': [2]}
    >>> merge_dicts(dict1, dict2)
    >>> dict1
    {'a': 'b', 'c': [1, 2]}

    :param dict1: Primary dictionary which is merged into.
    :param dict2: Secondary dictionary for primary updates.
    :param force: Force overwriting concrete values in the
        primary dictionary with those from secondary.
    :param merge_list: Determines if merged or overwritten.
    :param merge_dict: Determines if merged or overwritten.
    """

    for key, value in dict2.items():

        if key not in dict1:
            dict1[key] = value

        elif (isinstance(dict1[key], list)
                and isinstance(value, list)
                and merge_list is True):

            dict1[key] = (
                [] + dict1[key] + value)

        elif (isinstance(dict1[key], dict)
                and isinstance(value, dict)
                and merge_dict is True):

            merge_dicts(
                dict1[key], value, force)

        elif force is True:
            dict1[key] = value



def sort_dict(
    value: dict[Any, Any],
    reverse: bool = False,
) -> dict[Any, Any]:
    """
    Sort the keys within the dictionary and return new one.

    Example
    -------
    >>> foo = {'b': 'be', 'a': 'ey'}
    >>> sort_dict(foo)
    {'a': 'ey', 'b': 'be'}
    >>> sort_dict(foo, True)
    {'b': 'be', 'a': 'ey'}

    :param value: Dictionary whose keys are sorted into new.
    :param reverse: Optionally reverse the sort direction.
    :returns: New dictionary with keys sorted alphabetical.
    """

    items = sorted(
        value.items(),
        reverse=reverse)

    return dict(items)
