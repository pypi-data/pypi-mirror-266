"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..common import config_load
from ..common import config_path
from ..common import config_paths
from ... import PROJECT
from ... import WORKSPACE



def test_config_load() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    loaded = config_load(
        'PROJECT/../.yamllint')

    assert list(loaded) == [
        'extends', 'rules']



def test_config_path() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    path = config_path('PROJECT')

    assert path == PROJECT


    path = config_path('WORKSPACE')

    assert path == WORKSPACE



def test_config_paths() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    paths = config_paths([
        'PROJECT', 'WORKSPACE'])

    assert paths == (
        PROJECT, WORKSPACE)
