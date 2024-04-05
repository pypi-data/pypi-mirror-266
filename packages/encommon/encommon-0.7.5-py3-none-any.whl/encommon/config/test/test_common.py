"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..common import config_load
from ..common import config_path
from ... import PROJECT
from ... import WORKSPACE



def test_config_load() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    path = 'PROJECT/../.yamllint'

    assert len(config_load(path)) == 2



def test_config_path() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    assert config_path('PROJECT') == PROJECT
    assert config_path('WORKSPACE') == WORKSPACE
