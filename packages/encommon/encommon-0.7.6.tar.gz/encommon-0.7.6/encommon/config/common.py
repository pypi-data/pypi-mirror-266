"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from typing import Any
from typing import Literal
from typing import Optional

from yaml import SafeLoader
from yaml import load

from .. import PROJECT
from .. import WORKSPACE
from ..utils.common import PATHABLE
from ..utils.paths import resolve_path
from ..utils.paths import resolve_paths



LOGLEVELS = Literal[
    'critical',
    'debug',
    'error',
    'info',
    'warning']



def config_load(
    path: str | Path,
) -> dict[str, Any]:
    """
    Load configuration using the directory or file provided.

    :param path: Complete or relative path to configuration.
    :returns: New resolved filesystem path object instance.
    """

    loaded = (
        config_path(path)
        .read_text(encoding='utf-8'))

    parsed = load(loaded, SafeLoader)

    assert isinstance(parsed, dict)

    return parsed



def config_path(
    path: str | Path,
) -> Path:
    """
    Resolve the provided path and replace the magic keywords.

    .. note::
       This function simply wraps one from utils subpackage.

    :param path: Complete or relative path for processing.
    :returns: New resolved filesystem path object instance.
    """

    replace = {
        'PROJECT': str(PROJECT),
        'WORKSPACE': str(WORKSPACE)}

    return resolve_path(path, replace)



def config_paths(
    paths: PATHABLE,
    replace: Optional[dict[str, str]] = None,
) -> tuple[Path, ...]:
    """
    Resolve the provided paths and replace the magic keywords.

    .. note::
       This function simply wraps one from utils subpackage.

    :param paths: Complete or relative paths for processing.
    :returns: New resolved filesystem path object instances.
    """

    replace = {
        'PROJECT': str(PROJECT),
        'WORKSPACE': str(WORKSPACE)}

    return resolve_paths(paths, replace)
