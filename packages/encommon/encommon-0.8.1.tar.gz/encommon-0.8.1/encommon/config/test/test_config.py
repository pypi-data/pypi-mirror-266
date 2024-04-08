"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from typing import TYPE_CHECKING

from . import SAMPLES
from ..logger import Logger
from ..params import Params
from ... import ENPYRWS
from ... import PROJECT
from ...crypts import Crypts
from ...utils import load_sample
from ...utils import prep_sample

if TYPE_CHECKING:
    from ..config import Config



def test_Config(
    tmp_path: Path,
    config: 'Config',
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param tmp_path: pytest object for temporal filesystem.
    :param config: Primary class instance for configuration.
    """


    attrs = list(config.__dict__)

    assert attrs == [
        '_Config__model',
        '_Config__files',
        '_Config__cargs',
        '_Config__params',
        '_Config__paths',
        '_Config__logger',
        '_Config__crypts']


    assert repr(config)[:23] == (
        '<encommon.config.config')

    assert hash(config) > 0

    assert str(config)[:23] == (
        '<encommon.config.config')


    assert 'ConfigFiles' in str(config.files)

    assert 'ConfigPaths' in str(config.paths)

    assert len(config.cargs) == 1

    assert len(config.config) == 3

    assert config.model is Params

    assert isinstance(config.params, Params)

    assert isinstance(config.logger, Logger)

    assert isinstance(config.crypts, Crypts)


    replaces = {
        'pytemp': tmp_path,
        'PROJECT': PROJECT}

    sample_path = (
        f'{SAMPLES}/config.json')

    sample = load_sample(
        path=sample_path,
        update=ENPYRWS,
        content=config.config,
        replace=replaces)

    expect = prep_sample(
        content=config.config,
        replace=replaces)

    assert sample == expect



def test_Config_cover(
    config: 'Config',
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config: Primary class instance for configuration.
    """


    logger1 = config.logger
    logger2 = config.logger

    assert logger1 is logger2


    crypts1 = config.crypts
    crypts2 = config.crypts

    assert crypts1 is crypts2
