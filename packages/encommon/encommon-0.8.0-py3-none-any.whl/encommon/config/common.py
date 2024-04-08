"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path
from typing import Any
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING

from yaml import SafeLoader
from yaml import load

from .. import PROJECT
from .. import WORKSPACE
from ..utils import read_text
from ..utils import resolve_path
from ..utils import resolve_paths

if TYPE_CHECKING:
    from ..utils.common import PATHABLE
    from ..utils.common import REPLACE



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

    loaded = read_text(
        config_path(path))

    parsed = load(loaded, SafeLoader)

    assert isinstance(parsed, dict)

    return parsed



def config_path(
    path: str | Path,
) -> Path:
    """
    Resolve the provided path replacing the magic keywords.

    .. note::
       This function simply wraps one from utils subpackage.

    :param path: Complete or relative path for processing.
    :returns: New resolved filesystem path object instance.
    """

    replace = {
        'PROJECT': PROJECT,
        'WORKSPACE': WORKSPACE}

    return resolve_path(path, replace)



def config_paths(
    paths: 'PATHABLE',
    replace: Optional['REPLACE'] = None,
) -> tuple[Path, ...]:
    """
    Resolve the provided paths replacing the magic keywords.

    .. note::
       This function simply wraps one from utils subpackage.

    :param paths: Complete or relative paths for processing.
    :returns: New resolved filesystem path object instances.
    """

    replace = {
        'PROJECT': PROJECT,
        'WORKSPACE': WORKSPACE}

    return resolve_paths(paths, replace)
