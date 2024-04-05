"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from . import SAMPLES
from ..paths import ConfigPath
from ..paths import ConfigPaths
from ... import ENPYRWS
from ...utils.sample import load_sample
from ...utils.sample import prep_sample



def test_ConfigPath(
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    path = ConfigPath(config_path)

    attrs = list(path.__dict__)

    assert attrs == ['path', 'config']


    assert repr(path).startswith(
        '<encommon.config.paths.ConfigPath')
    assert isinstance(hash(path), int)
    assert str(path).startswith(
        '<encommon.config.paths.ConfigPath')


    assert path.path == config_path
    assert len(path.config) == 2



def test_ConfigPaths(
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    paths = ConfigPaths(config_path)

    attrs = list(paths.__dict__)

    assert attrs == [
        'paths', 'config',
        '_ConfigPaths__merged']


    assert repr(paths).startswith(
        '<encommon.config.paths.ConfigPaths')
    assert isinstance(hash(paths), int)
    assert str(paths).startswith(
        '<encommon.config.paths.ConfigPaths')


    assert len(paths.paths) == 1
    assert len(paths.config) == 1


    _merged1 = paths.merged
    _merged2 = paths.merged

    assert _merged1 is not _merged2

    sample_path = Path(
        f'{SAMPLES}/paths.json')

    sample = load_sample(
        path=sample_path,
        update=ENPYRWS,
        content=_merged1,
        replace={
            'config_path': str(config_path)})

    expect = prep_sample(
        content=_merged2,
        replace={
            'config_path': str(config_path)})

    assert sample == expect
