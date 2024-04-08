"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pathlib import Path

from _pytest.logging import LogCaptureFixture

from pytest import fixture

from ..logger import Logger
from ..logger import Message
from ..params import LoggerParams
from ...times.common import UNIXMPOCH
from ...times.common import UNIXSPOCH
from ...utils import strip_ansi



_CAPLOG = list[tuple[str, int, str]]



@fixture
def logger(
    tmp_path: Path,
) -> Logger:
    """
    Construct the instance for use in the downstream tests.

    :param tmp_path: pytest object for temporal filesystem.
    :returns: Newly constructed instance of related class.
    """

    params = LoggerParams(
        stdo_level='info',
        file_level='info',
        file_path=f'{tmp_path}/test.log')

    return Logger(params=params)



def test_Message() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    message = Message(
        time=UNIXMPOCH,
        level='info',
        string='foobar',
        none=None,
        list=['1', 2],
        tuple=('1', 2),
        set={'1', 2},
        dict={'1': 2},
        empty_list=[],
        empty_dict={},
        int=1,
        float=2.0,
        elapsed=3.69420)


    attrs = list(message.__dict__)

    assert attrs == [
        '_Message__level',
        '_Message__time',
        '_Message__fields']


    assert repr(message)[:20] == (
        'Message(level="info"')

    assert hash(message) > 0

    assert str(message)[:20] == (
        'Message(level="info"')


    assert message.level == 'info'

    assert message.time == 0

    assert len(message.fields) == 8


    output = strip_ansi(
        message.stdo_output)

    assert output == (
        'level="info"'
        f' time="{UNIXSPOCH}"'
        ' string="foobar"'
        ' list="1,2"'
        ' tuple="1,2"'
        ' set="1,2"'
        ' dict="{\'1\': 2}"'
        ' int="1"'
        ' float="2.0"'
        ' elapsed="3.69"')


    output = message.file_output

    assert output == (
        '{"level": "info",'
        f' "time": "{UNIXMPOCH}",'
        ' "string": "foobar",'
        ' "list": "1,2",'
        ' "tuple": "1,2",'
        ' "set": "1,2",'
        ' "dict": "{\'1\': 2}",'
        ' "int": "1",'
        ' "float": "2.0",'
        ' "elapsed": "3.69"}')



def test_Logger(
    logger: Logger,
    caplog: LogCaptureFixture,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param logger: Custom fixture for the logger instance.
    :param caplog: pytest object for capturing log message.
    """


    attrs = list(logger.__dict__)

    assert attrs == [
        '_Logger__stdo_level',
        '_Logger__file_level',
        '_Logger__file_path',
        '_Logger__started',
        '_Logger__logr_stdo',
        '_Logger__logr_file']


    assert repr(logger)[:23] == (
        '<encommon.config.logger')

    assert hash(logger) > 0

    assert str(logger)[:23] == (
        '<encommon.config.logger')


    assert logger.stdo_level == 'info'

    assert logger.file_level == 'info'

    assert logger.file_path is not None

    assert logger.started is False

    assert logger.logger_stdo is not None

    assert logger.logger_file is not None


    logger.log_d(msg='pytest')
    logger.log_c(msg='pytest')
    logger.log_e(msg='pytest')
    logger.log_i(msg='pytest')
    logger.log_w(msg='pytest')



def test_Logger_cover(
    logger: Logger,
    caplog: LogCaptureFixture,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param logger: Custom fixture for the logger instance.
    :param caplog: pytest object for capturing log message.
    """


    def _logger_logs() -> None:
        logger.log_d(msg='pytest')
        logger.log_c(msg='pytest')
        logger.log_e(msg='pytest')
        logger.log_i(msg='pytest')
        logger.log_w(msg='pytest')


    def _logger_stdo() -> _CAPLOG:

        output = caplog.record_tuples
        key = 'encommon.logger.stdo'

        return [
            x for x in output
            if x[0] == key]


    def _logger_file() -> _CAPLOG:

        output = caplog.record_tuples
        key = 'encommon.logger.file'

        return [
            x for x in output
            if x[0] == key]


    logger.start()

    _logger_logs()

    assert len(_logger_stdo()) == 5
    assert len(_logger_file()) == 5

    logger.stop()


    _logger_logs()

    assert len(_logger_stdo()) == 5
    assert len(_logger_file()) == 5


    logger.start()

    message = 'unknown exception'
    raises = Exception('pytest')

    logger.log_e(
        message=message,
        exc_info=raises)

    stdo = _logger_stdo()[-1][2]
    file = _logger_file()[-1][2]

    assert message in str(stdo)
    assert message in str(file)

    assert len(_logger_stdo()) == 6
    assert len(_logger_file()) == 6

    logger.stop()


    _logger_logs()

    assert len(_logger_stdo()) == 6
    assert len(_logger_file()) == 6
