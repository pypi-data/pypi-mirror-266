"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from . import SAMPLES
from ..files import ConfigFile
from ..files import ConfigFiles
from ... import ENPYRWS
from ...utils.sample import load_sample
from ...utils.sample import prep_sample



def test_ConfigFile(
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    file = ConfigFile(
        f'{config_path}/wayne/bwayne.yml')

    attrs = list(file.__dict__)

    assert attrs == ['path', 'config']


    assert repr(file).startswith(
        '<encommon.config.files.ConfigFile')
    assert isinstance(hash(file), int)
    assert str(file).startswith(
        '<encommon.config.files.ConfigFile')


    assert file.path.name == 'bwayne.yml'
    assert list(file.config) == ['name']



def test_ConfigFiles(
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    files = ConfigFiles([
        f'{config_path}/wayne/bwayne.yml',
        f'{config_path}/stark/tstark.yml'])

    attrs = list(files.__dict__)

    assert attrs == [
        'paths', 'config',
        '_ConfigFiles__merged']


    assert repr(files).startswith(
        '<encommon.config.files.ConfigFiles')
    assert isinstance(hash(files), int)
    assert str(files).startswith(
        '<encommon.config.files.ConfigFiles')


    assert len(files.paths) == 2
    assert len(files.config) == 2


    files = ConfigFiles(
        f'{config_path}/wayne/bwayne.yml')


    _merged1 = files.merged
    _merged2 = files.merged

    assert _merged1 is not _merged2

    sample_path = Path(
        f'{SAMPLES}/files.json')

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
