"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from pytest import fixture

from .config import Config
from .config.test import SAMPLES
from .utils import save_text



def config_factory(
    tmp_path: Path,
) -> Config:
    """
    Construct the instance for use in the downstream tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: Newly constructed instance of related class.
    """

    save_text(
        f'{tmp_path}/config.yml',
        content=(
            'enconfig:\n'
            '  paths:\n'
            f"    - '{SAMPLES}/stark'\n"
            f"    - '{SAMPLES}/wayne'\n"
            'enlogger:\n'
            '  stdo_level: info\n'
            'encrypts:\n'
            '  phrases:\n'
            '    default: phrase\n'))

    config_log = f'{tmp_path}/config.log'

    cargs = {
        'enlogger': {
            'file_path': config_log,
            'file_level': 'info'}}

    return Config(
        files=f'{tmp_path}/config.yml',
        cargs=cargs)



@fixture
def config_path(
    tmp_path: Path,
) -> Path:
    """
    Construct the directory and files needed for the tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: New resolved filesystem path object instance.
    """

    config_factory(tmp_path)

    return tmp_path.resolve()



@fixture
def config(
    tmp_path: Path,
) -> Config:
    """
    Construct the instance for use in the downstream tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: Newly constructed instance of related class.
    """

    return config_factory(tmp_path)
