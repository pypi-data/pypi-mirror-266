"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from pytest import fixture

from . import SAMPLES
from ..files import ConfigFile
from ..files import ConfigFiles



@fixture
def files(
    config_path: Path,
) -> ConfigFiles:
    """
    Construct the instance for use in the downstream tests.

    :param config_path: Custom fixture for populating paths.
    :returns: Newly constructed instance of related class.
    """

    return ConfigFiles([
        f'{SAMPLES}/wayne/bwayne.yml',
        f'{SAMPLES}/stark/tstark.yml'])



def test_ConfigFile(
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    file = ConfigFile(
        f'{config_path}/config.yml')


    attrs = list(file.__dict__)

    assert attrs == [
        'path',
        'config']


    assert repr(file)[:22] == (
        '<encommon.config.files')

    assert hash(file) > 0

    assert str(file)[:22] == (
        '<encommon.config.files')


    assert file.path.name == 'config.yml'

    assert len(file.config) == 3



def test_ConfigFiles(
    files: ConfigFiles,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param files: Custom fixture for the configuration files.
    """


    attrs = list(files.__dict__)

    assert attrs == [
        'paths',
        'config',
        '_ConfigFiles__merged']


    assert repr(files)[:22] == (
        '<encommon.config.files')

    assert hash(files) > 0

    assert str(files)[:22] == (
        '<encommon.config.files')


    assert len(files.paths) == 2

    assert len(files.config) == 2

    assert files.merged == {
        'name': 'Bruce Wayne'}



def test_ConfigFiles_cover(
    files: ConfigFiles,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param files: Custom fixture for the configuration files.
    """

    merged1 = files.merged
    merged2 = files.merged

    assert merged1 is not merged2
