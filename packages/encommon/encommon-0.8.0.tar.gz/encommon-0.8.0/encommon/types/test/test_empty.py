"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import copy
from copy import deepcopy

from ..empty import Empty
from ..empty import EmptyType



def test_EmptyType() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    empty = EmptyType()


    attrs = list(empty.__dict__)

    assert attrs == [
        '_EmptyType__empty']


    assert repr(empty) == 'Empty'
    assert hash(empty) > 0
    assert str(empty) == 'Empty'


    assert not (Empty or None)
    assert Empty is empty
    assert Empty is Empty
    assert Empty is EmptyType()
    assert Empty == empty
    assert Empty == Empty
    assert Empty == EmptyType()
    assert Empty is not None
    assert Empty != 'Empty'

    assert deepcopy(Empty) is Empty
    assert copy(Empty) is Empty
