"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from pytest import fixture



@fixture
def config_path(
    tmp_path: Path,
) -> Path:
    """
    Construct the directory and files needed for the tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: New resolved filesystem path object instance.
    """


    Path.mkdir(
        Path(f'{tmp_path}/wayne'))

    (Path(f'{tmp_path}/wayne')
        .joinpath('bwayne.yml')
        .write_text('name: Bruce Wayne'))


    Path.mkdir(
        Path(f'{tmp_path}/stark'))

    (Path(f'{tmp_path}/stark')
        .joinpath('tstark.yml')
        .write_text('name: Tony Stark'))


    return tmp_path.resolve()
