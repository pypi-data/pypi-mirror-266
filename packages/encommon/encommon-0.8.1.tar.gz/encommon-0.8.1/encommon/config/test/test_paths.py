"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from pytest import fixture

from . import SAMPLES
from ..paths import ConfigPath
from ..paths import ConfigPaths
from ... import ENPYRWS
from ... import PROJECT
from ...utils import load_sample
from ...utils import prep_sample



@fixture
def paths(
    config_path: Path,
) -> ConfigPaths:
    """
    Construct the instance for use in the downstream tests.

    :param config_path: Custom fixture for populating paths.
    :returns: Newly constructed instance of related class.
    """

    return ConfigPaths([
        f'{SAMPLES}/stark',
        f'{SAMPLES}/wayne'])



def test_ConfigPath(
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    path = ConfigPath(config_path)


    attrs = list(path.__dict__)

    assert attrs == [
        'path',
        'config']


    assert repr(path)[:22] == (
        '<encommon.config.paths')

    assert hash(path) > 0

    assert str(path)[:22] == (
        '<encommon.config.paths')


    assert 'test' in path.path.name

    assert len(path.config) == 1



def test_ConfigPaths(
    paths: ConfigPaths,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param paths: Custom fixture for the configuration paths.
    """


    attrs = list(paths.__dict__)

    assert attrs == [
        'paths', 'config',
        '_ConfigPaths__merged']


    assert repr(paths)[:22] == (
        '<encommon.config.paths')

    assert hash(paths) > 0

    assert str(paths)[:22] == (
        '<encommon.config.paths')


    assert len(paths.paths) == 2

    assert len(paths.config) == 2


    replaces = {
        'PROJECT': PROJECT}

    sample_path = (
        f'{SAMPLES}/paths.json')

    sample = load_sample(
        path=sample_path,
        update=ENPYRWS,
        content=paths.merged,
        replace=replaces)

    expect = prep_sample(
        content=paths.merged,
        replace=replaces)

    assert sample == expect



def test_ConfigPaths_cover(
    paths: ConfigPaths,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param paths: Custom fixture for the configuration paths.
    """

    merged1 = paths.merged
    merged2 = paths.merged

    assert merged1 is not merged2
