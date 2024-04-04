"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from . import SAMPLES
from ..config import Config
from ..logger import Logger
from ..params import Params
from ... import ENPYRWS
from ...crypts.crypts import Crypts
from ...utils.sample import load_sample
from ...utils.sample import prep_sample



def test_Config(  # noqa: CFQ001
    config_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param config_path: Custom fixture for populating paths.
    """

    (config_path
        .joinpath('one.yml')
        .write_text(
            'enconfig:\n'
            f'  paths: ["{config_path}"]\n'
            'enlogger:\n'
            '  stdo_level: info\n'))

    (config_path
        .joinpath('two.yml')
        .write_text(
            'encrypts:\n'
            '  phrases:\n'
            '    default: fernetphrase\n'
            'enlogger:\n'
            '  stdo_level: debug\n'
            '  file_level: info\n'))


    config = Config(
        files=[
            f'{config_path}/one.yml',
            f'{config_path}/two.yml'],
        cargs={
            'enlogger': {
                'file_level': 'warning'}})

    attrs = list(config.__dict__)

    assert attrs == [
        '_Config__model',
        '_Config__files',
        '_Config__cargs',
        '_Config__params',
        '_Config__paths',
        '_Config__logger',
        '_Config__crypts']


    assert repr(config).startswith(
        '<encommon.config.config.Config')
    assert isinstance(hash(config), int)
    assert str(config).startswith(
        '<encommon.config.config.Config')


    assert len(config.files.paths) == 2
    assert len(config.paths.paths) == 1
    assert len(config.cargs) == 1
    assert isinstance(config.config, dict)
    assert config.model is Params
    assert isinstance(config.params, Params)


    _config1 = config.config
    _config2 = config.config

    assert _config1 is not _config2


    sample_path = Path(
        f'{SAMPLES}/config.json')

    sample = load_sample(
        path=sample_path,
        update=ENPYRWS,
        content=_config1,
        replace={
            'config_path': str(config_path)})

    expect = prep_sample(
        content=_config2,
        replace={
            'config_path': str(config_path)})

    assert sample == expect


    _params1 = config.params
    _params2 = config.params

    assert _params1 is _params2


    sample_path = Path(
        f'{SAMPLES}/params.json')

    sample = load_sample(
        path=sample_path,
        update=ENPYRWS,
        content=_params1.model_dump(),
        replace={
            'config_path': str(config_path)})

    expect = prep_sample(
        content=_params2.model_dump(),
        replace={
            'config_path': str(config_path)})

    assert sample == expect


    logger = config.logger

    assert isinstance(logger, Logger)

    _logger1 = config.logger
    _logger2 = config.logger

    assert _logger1 is _logger2


    crypts = config.crypts

    assert isinstance(crypts, Crypts)

    _crypts1 = config.crypts
    _crypts2 = config.crypts

    assert _crypts1 is _crypts2
