"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..strings import striplower



def test_striplower() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    assert striplower(' Foo ') == 'foo'
