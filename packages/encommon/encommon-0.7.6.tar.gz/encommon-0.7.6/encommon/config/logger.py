"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from json import dumps
from logging import CRITICAL
from logging import DEBUG
from logging import ERROR
from logging import FileHandler
from logging import Formatter
from logging import INFO
from logging import Logger as _Logger
from logging import NOTSET
from logging import NullHandler
from logging import StreamHandler
from logging import WARNING
from logging import getLogger
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Optional
from typing import TYPE_CHECKING

from .common import LOGLEVELS
from .common import config_path
from ..times.common import PARSABLE
from ..times.times import Times
from ..types.empty import Empty
from ..utils.stdout import kvpair_ansi

if TYPE_CHECKING:
    from .params import LoggerParams



LOGGER_FILE = 'encommon.logger.file'
LOGGER_STDO = 'encommon.logger.stdo'

LOGSEVERS = {
    'critical': int(CRITICAL),
    'debug': int(DEBUG),
    'error': int(ERROR),
    'info': int(INFO),
    'warning': int(WARNING)}



class Message:
    """
    Format the provided keyword arguments for logging output.

    .. note::
       Log messages are expected to contain string or numeric.

    .. testsetup::
       >>> from encommon.utils.stdout import strip_ansi

    Example
    -------
    >>> message = Message('info', '1970-01-01', foo='bar')
    >>> strip_ansi(message.stdo_output)
    'level="info" time="1970-01-01T00:00:00Z" foo="bar"'

    :param level: Severity which log message is classified.
    :param time: What time the log message actually occurred.
    :param kwargs: Keyword arguments for populating message.
    """

    __level: LOGLEVELS
    __time: Times
    __fields: dict[str, str] = {}


    def __init__(
        self,
        level: LOGLEVELS,
        time: Optional[PARSABLE] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.__level = level
        self.__time = Times(time)
        self.__fields = {}

        for key, value in kwargs.items():

            if (hasattr(value, '__len__')
                    and not len(value)):
                continue

            if value in [None, Empty]:
                continue

            if (key == 'elapsed'
                    and isinstance(value, float)):
                value = round(value, 2)

            value = str(value)

            self.__fields[key] = value


    def __repr__(
        self,
    ) -> str:
        """
        Built-in method for representing the values for instance.

        :returns: String representation for values from instance.
        """

        fields: dict[str, str] = {
            'level': self.__level,
            'time': self.__time.subsec}

        fields |= dict(self.__fields)

        message = ', '.join([
            f'{k}="{v}"' for k, v
            in fields.items()])

        return f'Message({message})'


    def __str__(
        self,
    ) -> str:
        """
        Built-in method for representing the values for instance.

        :returns: String representation for values from instance.
        """

        return self.__repr__()


    @property
    def level(
        self,
    ) -> LOGLEVELS:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__level


    @property
    def time(
        self,
    ) -> Times:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return Times(self.__time)


    @property
    def fields(
        self,
    ) -> dict[str, str]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return dict(self.__fields)


    @property
    def stdo_output(
        self,
    ) -> str:
        """
        Format keyword arguments for writing to standard output.

        :returns: String representation for the standard output.
        """

        fields: dict[str, str] = {
            'level': self.__level,
            'time': self.__time.simple}

        fields |= dict(self.__fields)


        fields['time'] = (
            fields['time']
            .replace('+0000', 'Z'))


        output: list[str] = []

        for key, value in fields.items():
            output.append(
                kvpair_ansi(key, value))

        return ' '.join(output)


    @property
    def file_output(
        self,
    ) -> str:
        """
        Format keyword arguments for writing to filesystem path.

        :returns: String representation for the filesystem path.
        """

        fields: dict[str, str] = {
            'level': self.__level,
            'time': self.__time.subsec}

        fields |= dict(self.__fields)


        return dumps(fields)



class FileFormatter(Formatter):
    """
    Supplement class for built-in logging exception formatter.
    """


    def formatException(
        self,
        ei: Any,  # noqa: ANN401
    ) -> str:
        """
        Specifically overrides method for formatting exceptions.

        :param ei: Exception information provided by the logger.
        """

        reason = super().formatException(ei)

        message = Message(
            level='error',
            status='exception',
            reason=reason)

        return message.file_output



class Logger:
    """
    Manage the file and standard output with logging library.

    .. note::
       Uses keyword name for levels in Pyton logging library.

    +-----------+-----------+
    | *Numeric* | *Keyword* |
    +-----------+-----------+
    | 10        | debug     |
    +-----------+-----------+
    | 20        | info      |
    +-----------+-----------+
    | 30        | warning   |
    +-----------+-----------+
    | 40        | error     |
    +-----------+-----------+
    | 50        | critical  |
    +-----------+-----------+

    Example
    -------
    >>> logger = Logger(stdo_level='info')
    >>> logger.start()
    >>> logger.log_i(message='testing')

    :param stdo_level: Minimum level for the message to pass.
    :param file_level: Minimum level for the message to pass.
    :param file_path: Enables writing to the filesystem path.
    :param params: Parameters for instantiating the instance.
    """

    __stdo_level: Optional[LOGLEVELS]
    __file_level: Optional[LOGLEVELS]
    __file_path: Optional[Path]

    __started: bool

    __logger_stdo: _Logger
    __logger_file: _Logger


    def __init__(
        self,
        *,
        stdo_level: Optional[LOGLEVELS] = None,
        file_level: Optional[LOGLEVELS] = None,
        file_path: Optional[str | Path] = None,
        params: Optional['LoggerParams'] = None,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        if params is not None:
            stdo_level = params.stdo_level
            file_level = params.file_level
            file_path = params.file_path

        if file_path is not None:
            file_path = config_path(file_path)

        self.__stdo_level = stdo_level
        self.__file_level = file_level
        self.__file_path = file_path

        self.__started = False

        self.__logger_stdo = getLogger(LOGGER_STDO)
        self.__logger_file = getLogger(LOGGER_FILE)


    @property
    def stdo_level(
        self,
    ) -> Optional[LOGLEVELS]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__stdo_level


    @property
    def file_level(
        self,
    ) -> Optional[LOGLEVELS]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__file_level


    @property
    def file_path(
        self,
    ) -> Optional[Path]:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__file_path


    @property
    def started(
        self,
    ) -> bool:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__started


    @property
    def logger_stdo(
        self,
    ) -> _Logger:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__logger_stdo


    @property
    def logger_file(
        self,
    ) -> _Logger:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__logger_file


    def start(
        self,
    ) -> None:
        """
        Initialize the Python logging library using parameters.
        """

        stdo_level = self.__stdo_level
        file_level = self.__file_level
        file_path = self.__file_path

        logger_stdo = self.__logger_stdo
        logger_file = self.__logger_file


        logger_root = getLogger()
        logger_root.setLevel(NOTSET)

        logger_stdo.handlers = [NullHandler()]
        logger_file.handlers = [NullHandler()]


        if stdo_level is not None:

            stdoh = StreamHandler()
            format = Formatter('%(message)s')
            level = LOGSEVERS[stdo_level]

            stdoh.setLevel(level)
            stdoh.setFormatter(format)

            logger_stdo.handlers = [stdoh]


        if file_path and file_level:

            fileh = FileHandler(file_path)
            format = FileFormatter('%(message)s')
            level = LOGSEVERS[file_level]

            fileh.setLevel(level)
            fileh.setFormatter(format)

            logger_file.handlers = [fileh]


        self.__started = True


    def stop(
        self,
    ) -> None:
        """
        Deinitialize the Python logging library using parameters.
        """

        logger_stdo = self.__logger_stdo
        logger_file = self.__logger_file

        logger_stdo.handlers = [NullHandler()]
        logger_file.handlers = [NullHandler()]

        self.__started = False


    def log(
        self,
        level: Literal[LOGLEVELS],
        *,
        exc_info: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prepare keyword arguments and log to the relevant outputs.

        :param exc_info: Optional exception to include with trace.
        :param kwargs: Keyword arguments for populating message.
        """

        if self.__started is False:
            return

        stdo_level = self.__stdo_level
        file_level = self.__file_level
        file_path = self.__file_path

        logger_stdo = self.__logger_stdo
        logger_file = self.__logger_file

        message = Message(level, **kwargs)

        if stdo_level is not None:
            logger_stdo.log(
                level=LOGSEVERS[level],
                msg=message.stdo_output,
                exc_info=exc_info)

        if file_path and file_level:
            logger_file.log(
                level=LOGSEVERS[level],
                msg=message.file_output,
                exc_info=exc_info)


    def log_c(
        self,
        *,
        exc_info: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prepare keyword arguments and log to the relevant outputs.

        :param exc_info: Optional exception to include with trace.
        :param kwargs: Keyword arguments for populating message.
        """

        self.log(
            level='critical',
            exc_info=exc_info,
            **kwargs)


    def log_d(
        self,
        *,
        exc_info: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prepare keyword arguments and log to the relevant outputs.

        :param exc_info: Optional exception to include with trace.
        :param kwargs: Keyword arguments for populating message.
        """

        self.log(
            level='debug',
            exc_info=exc_info,
            **kwargs)


    def log_e(
        self,
        *,
        exc_info: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prepare keyword arguments and log to the relevant outputs.

        :param exc_info: Optional exception to include with trace.
        :param kwargs: Keyword arguments for populating message.
        """

        self.log(
            level='error',
            exc_info=exc_info,
            **kwargs)


    def log_i(
        self,
        *,
        exc_info: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prepare keyword arguments and log to the relevant outputs.

        :param exc_info: Optional exception to include with trace.
        :param kwargs: Keyword arguments for populating message.
        """

        self.log(
            level='info',
            exc_info=exc_info,
            **kwargs)


    def log_w(
        self,
        *,
        exc_info: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """
        Prepare keyword arguments and log to the relevant outputs.

        :param exc_info: Optional exception to include with trace.
        :param kwargs: Keyword arguments for populating message.
        """

        self.log(
            level='warning',
            exc_info=exc_info,
            **kwargs)
