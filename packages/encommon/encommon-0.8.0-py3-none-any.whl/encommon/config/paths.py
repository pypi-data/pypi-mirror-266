"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import deepcopy
from glob import glob
from pathlib import Path
from typing import Any
from typing import Optional
from typing import TYPE_CHECKING

from .common import config_path
from .common import config_paths
from .files import ConfigFile

if TYPE_CHECKING:
    from ..utils.common import PATHABLE



class ConfigPath:
    """
    Contain the configuration content from filesystem path.

    :param path: Complete or relative path to configuration.
    """

    path: Path
    config: dict[str, ConfigFile]


    def __init__(
        self,
        path: str | Path,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.path = config_path(path)

        glob_path = [
            f'{self.path}/*.yml',
            f'{self.path}/**/*.yml']

        self.config = {
            str(y): ConfigFile(y)
            for x in glob_path
            for y in glob(x, recursive=True)}



class ConfigPaths:
    """
    Enumerate paths and store the contents on relative path.

    .. note::
       Class can be empty in order to play nice with parent.

    :param paths: Complete or relative path to config paths.
    :param force: Force the merge on earlier files by later.
    """

    paths: tuple[Path, ...]
    config: dict[str, ConfigPath]

    __merged: Optional[dict[str, Any]]


    def __init__(
        self,
        paths: 'PATHABLE',
        force: bool = False,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.paths = config_paths(paths)

        self.config = {
            str(x): ConfigPath(x)
            for x in self.paths}

        self.__merged = None


    @property
    def merged(
        self,
    ) -> dict[str, Any]:
        """
        Return the configuration in dictionary format for paths.

        :returns: Configuration in dictionary format for paths.
        """

        config = self.config
        merged = self.__merged

        if merged is not None:
            return deepcopy(merged)

        merged = {}


        for path in config.values():

            items = path.config.items()

            for key, file in items:

                merged[key] = file.config


        self.__merged = merged

        return deepcopy(merged)
