"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from logging import Logger as _Logger
from pathlib import Path

from _pytest.logging import LogCaptureFixture

from ..logger import Logger
from ..logger import Message
from ...times.common import UNIXMPOCH
from ...utils.stdout import strip_ansi



def test_Message() -> None:
    """
    Perform various tests associated with relevant routines.
    """


    message = Message(
        time=UNIXMPOCH,
        level='info',
        dict={'foo': 'bar'},
        empty=[],
        float=1.0,
        int=1,
        list=[1, '2', 3],
        none=None,
        string='foo',
        elapsed=0.69420)

    attrs = list(message.__dict__)

    assert attrs == [
        '_Message__level',
        '_Message__time',
        '_Message__fields']


    assert repr(message).startswith(
        'Message(level="info", time="1970')
    assert isinstance(hash(message), int)
    assert str(message).startswith(
        'Message(level="info", time="1970')


    assert repr(message) == (
        'Message('
        'level="info", '
        f'time="{UNIXMPOCH}", '
        'dict="{\'foo\': \'bar\'}", '
        'float="1.0", '
        'int="1", '
        'list="[1, \'2\', 3]", '
        'string="foo", '
        'elapsed="0.69")')

    assert str(message) == repr(message)


    assert message.level == 'info'
    assert message.time == '1970-01-01'

    assert message.fields == {
        'dict': "{'foo': 'bar'}",
        'float': '1.0',
        'int': '1',
        'list': "[1, '2', 3]",
        'string': 'foo',
        'elapsed': '0.69'}


    output = strip_ansi(message.stdo_output)

    assert output == (
        'level="info"'
        ' time="1970-01-01T00:00:00Z"'
        ' dict="{\'foo\': \'bar\'}"'
        ' float="1.0"'
        ' int="1"'
        ' list="[1, \'2\', 3]"'
        ' string="foo"'
        ' elapsed="0.69"')


    assert message.file_output == (
        '{"level": "info",'
        f' "time": "{UNIXMPOCH}",'
        ' "dict": "{\'foo\': \'bar\'}",'
        ' "float": "1.0",'
        ' "int": "1",'
        ' "list": "[1, \'2\', 3]",'
        ' "string": "foo",'
        ' "elapsed": "0.69"}')



def test_Logger(
    tmp_path: Path,
    caplog: LogCaptureFixture,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param tmp_path: pytest object for temporal filesystem.
    :param caplog: pytest object for capturing log message.
    """


    logger = Logger(
        stdo_level='info',
        file_level='info',
        file_path=f'{tmp_path}/test.log')

    attrs = list(logger.__dict__)

    assert attrs == [
        '_Logger__stdo_level',
        '_Logger__file_level',
        '_Logger__file_path',
        '_Logger__started',
        '_Logger__logger_stdo',
        '_Logger__logger_file']


    assert repr(logger).startswith(
        '<encommon.config.logger.Logger')
    assert isinstance(hash(logger), int)
    assert str(logger).startswith(
        '<encommon.config.logger.Logger')


    assert logger.stdo_level == 'info'
    assert logger.file_level == 'info'
    assert logger.file_path is not None
    assert logger.file_path.name == 'test.log'
    assert logger.started is False
    assert isinstance(logger.logger_stdo, _Logger)
    assert isinstance(logger.logger_file, _Logger)


    def _logger_logs() -> None:
        logger.log_d(message='pytest')
        logger.log_c(message='pytest')
        logger.log_e(message='pytest')
        logger.log_i(message='pytest')
        logger.log_w(message='pytest')


    _caplog = list[tuple[str, int, str]]


    def _logger_stdo() -> _caplog:
        return [
            x for x in caplog.record_tuples
            if x[0] == 'encommon.logger.stdo']


    def _logger_file() -> _caplog:
        return [
            x for x in caplog.record_tuples
            if x[0] == 'encommon.logger.file']


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

    logger.log_e(
        message=message,
        exc_info=Exception('pytest'))

    stdo_text = _logger_stdo()[-1][2]
    file_text = _logger_file()[-1][2]

    assert message in str(stdo_text)
    assert message in str(file_text)

    assert len(_logger_stdo()) == 6
    assert len(_logger_file()) == 6

    logger.stop()


    _logger_logs()

    assert len(_logger_stdo()) == 6
    assert len(_logger_file()) == 6
