"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from ..common import read_text
from ..common import save_text



def test_readsave_text(
    tmp_path: Path,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param tmp_path: pytest object for temporal filesystem.
    """

    content = 'pytest'

    save_text(
        f'{tmp_path}/test.txt',
        content)

    loaded = read_text(
        f'{tmp_path}/test.txt')

    assert loaded == content
