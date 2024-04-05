"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from ..sample import load_sample
from ..sample import prep_sample
from ... import ENPYRWS
from ... import PROJECT



def test_prep_sample() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    assert prep_sample((1, '2')) == [1, '2']



def test_load_sample(
    tmp_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param tmp_path: pytest object for temporal filesystem.
    """

    path = (
        Path(tmp_path)
        .joinpath('samples.json'))

    source = {
        'list': ['bar', 'baz'],
        'tuple': (1, 2),
        'project': PROJECT,
        'other': '/path/to/other'}

    expect = {
        'list': ['bar', 'baz'],
        'tuple': [1, 2],
        'project': '_/encommon_sample/PROJECT/_',
        'other': '_/encommon_sample/tmp_path/_'}

    sample = load_sample(
        path=path,
        update=ENPYRWS,
        content=source,
        replace={'tmp_path': '/path/to/other'})

    assert sample == expect

    sample = load_sample(
        path=path,
        content=source | {'list': [1]},
        update=True,
        replace={'tmp_path': '/path/to/other'})

    assert sample == expect | {'list': [1]}
