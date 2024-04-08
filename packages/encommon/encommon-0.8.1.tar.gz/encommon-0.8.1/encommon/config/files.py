"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import deepcopy
from pathlib import Path
from typing import Any
from typing import Optional
from typing import TYPE_CHECKING

from .common import config_load
from .common import config_path
from .common import config_paths
from ..types import merge_dicts

if TYPE_CHECKING:
    from ..utils.common import PATHABLE



class ConfigFile:
    """
    Contain the configuration content from filesystem path.

    :param path: Complete or relative path to configuration.
    """

    path: Path
    config: dict[str, Any]


    def __init__(
        self,
        path: str | Path,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.path = config_path(path)
        self.config = config_load(path)



class ConfigFiles:
    """
    Enumerate files and store the contents on relative path.

    .. note::
       Class can be empty in order to play nice with parent.

    :param paths: Complete or relative path to config files.
    :param force: Force the merge on earlier files by later.
    """

    paths: tuple[Path, ...]
    config: dict[str, ConfigFile]

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
            str(x): ConfigFile(x)
            for x in self.paths}

        self.__merged = None


    @property
    def merged(
        self,
    ) -> dict[str, Any]:
        """
        Return the configuration in dictionary format for files.

        :returns: Configuration in dictionary format for files.
        """

        config = self.config
        merged = self.__merged

        if merged is not None:
            return deepcopy(merged)

        merged = {}


        for file in config.values():

            source = file.config

            merge_dicts(
                dict1=merged,
                dict2=deepcopy(source),
                force=False)


        self.__merged = merged

        return deepcopy(merged)
