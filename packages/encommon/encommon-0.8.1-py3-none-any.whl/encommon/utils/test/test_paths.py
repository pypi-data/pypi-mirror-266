"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import PosixPath

from ..paths import resolve_path
from ..paths import resolve_paths
from ..paths import stats_path
from ... import PROJECT
from ...times import Times



def test_resolve_path() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    path = resolve_path(
        path='/foo/bar',
        replace={'bar': 'foo'})

    assert path == (
        PosixPath('/foo/foo'))



def test_resolve_paths() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    paths = resolve_paths(
        paths='/foo/bar',
        replace={'bar': 'foo'})

    assert list(paths) == [
        PosixPath('/foo/foo')]


    paths = resolve_paths(
        paths=['/foo/bar', '/bar/foo'],
        replace={'bar': 'foo'})

    assert list(paths) == [
        PosixPath('/foo/foo')]



def test_stats_path() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    stats = stats_path(
        f'{PROJECT}/utils',
        replace={PROJECT: '/'},
        ignore=[r'\S+\.pyc'])

    stat = stats['/utils/paths.py']

    assert stat.st_ctime >= (
        Times('2023-01-01').epoch)
    assert stat.st_mtime >= (
        Times('2023-01-01').epoch)

    assert stat.st_size >= 2000

    assert list(stats) == [
        '/utils/__init__.py',
        '/utils/common.py',
        '/utils/match.py',
        '/utils/paths.py',
        '/utils/sample.py',
        '/utils/stdout.py',
        '/utils/test/__init__.py',
        '/utils/test/test_common.py',
        '/utils/test/test_match.py',
        '/utils/test/test_paths.py',
        '/utils/test/test_sample.py',
        '/utils/test/test_stdout.py']
