"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from copy import deepcopy
from typing import Any
from typing import Callable
from typing import Optional
from typing import TYPE_CHECKING

from .common import config_paths
from .files import ConfigFiles
from .logger import Logger
from .params import Params
from .paths import ConfigPaths
from ..crypts import Crypts
from ..types import merge_dicts

if TYPE_CHECKING:
    from ..utils.common import PATHABLE



class Config:
    """
    Contain the configurations from the arguments and files.

    .. note::
       Configuration loaded from files is validated with the
       Pydantic model :class:`.Params`.

    :param files: Complete or relative path to config files.
    :param paths: Complete or relative path to config paths.
    :param cargs: Configuration arguments in dictionary form,
        which will override contents from the config files.
    :param model: Override default config validation model.
    """

    __files: ConfigFiles
    __paths: ConfigPaths
    __cargs: dict[str, Any]

    __model: Callable  # type: ignore

    __params: Optional[Params]
    __logger: Optional[Logger]
    __crypts: Optional[Crypts]


    def __init__(
        self,
        *,
        files: Optional['PATHABLE'] = None,
        paths: Optional['PATHABLE'] = None,
        cargs: Optional[dict[str, Any]] = None,
        model: Optional[Callable] = None,  # type: ignore
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        files = files or []
        paths = paths or []
        cargs = cargs or {}

        paths = list(config_paths(paths))

        self.__model = model or Params
        self.__files = ConfigFiles(files)
        self.__cargs = deepcopy(cargs)

        self.__params = None

        enconfig = (
            self.params.enconfig)

        if enconfig and enconfig.paths:
            paths.extend(enconfig.paths)

        self.__paths = ConfigPaths(paths)

        self.__logger = None
        self.__crypts = None


    @property
    def files(
        self,
    ) -> ConfigFiles:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__files


    @property
    def paths(
        self,
    ) -> ConfigPaths:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__paths


    @property
    def cargs(
        self,
    ) -> dict[str, Any]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__cargs


    @property
    def config(
        self,
    ) -> dict[str, Any]:
        """
        Return the configuration in dictionary format for files.

        :returns: Configuration in dictionary format for files.
        """

        return self.params.model_dump()


    @property
    def model(
        self,
    ) -> Callable:  # type: ignore
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__model


    @property
    def params(
        self,
    ) -> Params:
        """
        Return the Pydantic model containing the configuration.

        :returns: Pydantic model containing the configuration.
        """

        if self.__params is not None:
            return self.__params

        cargs = self.__cargs
        merged = self.files.merged

        merge_dicts(
            dict1=merged,
            dict2=deepcopy(cargs),
            force=True)

        self.__params = (
            self.__model(**merged))

        return self.__params


    @property
    def logger(
        self,
    ) -> Logger:
        """
        Initialize the Python logging library using parameters.
        """

        if self.__logger is not None:
            return self.__logger

        enlogger = (
            self.params.enlogger)

        self.__logger = (
            Logger(params=enlogger))

        return self.__logger


    @property
    def crypts(
        self,
    ) -> Crypts:
        """
        Initialize the encryption instance using the parameters.
        """

        if self.__crypts is not None:
            return self.__crypts

        encrypts = (
            self.params.encrypts)

        self.__crypts = (
            Crypts(params=encrypts))

        return self.__crypts
