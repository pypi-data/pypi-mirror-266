"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import deepcopy

from ..dicts import merge_dicts
from ..dicts import sort_dict



_DICT1 = {
    'dict1': 'dict1',
    'str': 'd1string',
    'list': ['d1list'],
    'dict': {'key': 'd1value'},
    'bool': False}

_DICT2 = {
    'dict2': 'dict2',
    'str': 'd2string',
    'list': ['d2list'],
    'dict': {'key': 'd2value'},
    'bool': True}



def test_merge_dicts() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    dict1 = deepcopy(_DICT1)
    dict2 = deepcopy(_DICT2)

    dict1['recurse'] = deepcopy(dict1)
    dict2['recurse'] = deepcopy(dict2)


    source = deepcopy(dict1)
    update = deepcopy(dict2)

    merge_dicts(source, update)

    assert source == {
        'dict1': 'dict1',
        'dict2': 'dict2',
        'str': 'd1string',
        'list': ['d1list', 'd2list'],
        'dict': {'key': 'd1value'},
        'bool': False,
        'recurse': {
            'dict1': 'dict1',
            'dict2': 'dict2',
            'str': 'd1string',
            'list': ['d1list', 'd2list'],
            'dict': {'key': 'd1value'},
            'bool': False}}


    source = deepcopy(dict1)
    update = deepcopy(dict2)

    merge_dicts(source, update, True)

    assert source == {
        'dict1': 'dict1',
        'dict2': 'dict2',
        'str': 'd2string',
        'list': ['d1list', 'd2list'],
        'dict': {'key': 'd2value'},
        'bool': True,
        'recurse': {
            'dict1': 'dict1',
            'dict2': 'dict2',
            'str': 'd2string',
            'list': ['d1list', 'd2list'],
            'dict': {'key': 'd2value'},
            'bool': True}}


    source = deepcopy(dict1)
    update = deepcopy(dict2)

    merge_dicts(
        source,
        update,
        merge_list=False,
        merge_dict=False)

    assert source == {
        'dict1': 'dict1',
        'dict2': 'dict2',
        'str': 'd1string',
        'list': ['d1list'],
        'dict': {'key': 'd1value'},
        'bool': False,
        'recurse': {
            'dict1': 'dict1',
            'str': 'd1string',
            'list': ['d1list'],
            'dict': {'key': 'd1value'},
            'bool': False}}



def test_sort_dict() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    assert sort_dict(_DICT1) == {
        'bool': False,
        'dict': {'key': 'd1value'},
        'dict1': 'dict1',
        'list': ['d1list'],
        'str': 'd1string'}
