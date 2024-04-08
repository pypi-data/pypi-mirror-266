"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from _pytest.capture import CaptureFixture

from ..stdout import array_ansi
from ..stdout import kvpair_ansi
from ..stdout import make_ansi
from ..stdout import print_ansi
from ..stdout import strip_ansi
from ...times import Duration
from ...times import Times
from ...times.common import UNIXMPOCH
from ...types import Empty



def test_print_ansi(
    capsys: CaptureFixture[str],
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param capsys: pytest object for capturing print message.
    """

    print_ansi('<c91>test<c0>', 'print')

    output = capsys.readouterr().out

    assert strip_ansi(output) == 'test\n'



def test_make_ansi() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    output = make_ansi('<c31>test<c0>')

    assert output == (
        '\x1b[0;31mtest\x1b[0;0m')



def test_kvpair_ansi() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    output = kvpair_ansi('key', 'value')

    assert output == (
        '\x1b[0;90mkey\x1b[0;37m="\x1b'
        '[0;0mvalue\x1b[0;37m"\x1b[0;0m')

    output = kvpair_ansi('key', [1, 2])

    assert output == (
        '\x1b[0;90mkey\x1b[0;37m="\x1b'
        '[0;0m1,2\x1b[0;37m"\x1b[0;0m')

    output = kvpair_ansi('key', None)

    assert output == (
        '\x1b[0;90mkey\x1b[0;37m="\x1b'
        '[0;0mNone\x1b[0;37m"\x1b[0;0m')



def test_strip_ansi() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    output = '\x1b[0;31mtest\x1b[0;0m'

    assert strip_ansi(output) == 'test'



def test_array_ansi() -> None:  # noqa: CFQ001
    """
    Perform various tests associated with relevant routines.
    """

    simple = {
        'str': 'value',
        'list': [1, 2],
        'bool': False}

    repeat = {
        'dict': simple | {
            'dict': simple}}

    source = {
        'str': 'value',
        'int': 1,
        'float': 1.0,
        'complex': complex(3, 1),
        'list': [simple],
        'tuple': (simple,),
        'range': range(1, 3),
        'dict1': simple,
        'dict2': simple,
        'dict3': simple,
        'set': {1, 2, 3},
        'frozenset': {1, 2, 3},
        'bool': True,
        'none': None,
        '_private': None,
        'repeat': repeat,
        'Empty': Empty,
        'Duration': Duration(190802),
        'Times': Times(0)}


    output = strip_ansi(
        array_ansi(simple))

    assert output == (
        "str: 'value'\n"
        'list: list\n'
        '  - 1\n'
        '  - 2\n'
        'bool: False')


    output = strip_ansi(
        array_ansi([simple]))

    assert output == (
        '- dict\n'
        "  str: 'value'\n"
        '  list: list\n'
        '    - 1\n'
        '    - 2\n'
        '  bool: False')


    output = strip_ansi(
        array_ansi((1, 2, 3)))

    assert output == (
        '- 1\n'
        '- 2\n'
        '- 3')


    output = strip_ansi(
        array_ansi({1, 2, 3}))

    assert output == (
        '- 1\n'
        '- 2\n'
        '- 3')


    output = strip_ansi(
        array_ansi(source))

    assert output == (
        "str: 'value'\n"
        'int: 1\n'
        'float: 1.0\n'
        'complex: (3+1j)\n'
        'list: list\n'
        '  - dict\n'
        "    str: 'value'\n"
        '    list: list\n'
        '      - 1\n'
        '      - 2\n'
        '    bool: False\n'
        'tuple: tuple\n'
        '  - dict\n'
        "    str: 'value'\n"
        '    list: list\n'
        '      - 1\n'
        '      - 2\n'
        '    bool: False\n'
        'range: range(1, 3)\n'
        'dict1: dict\n'
        "  str: 'value'\n"
        '  list: list\n'
        '    - 1\n'
        '    - 2\n'
        '  bool: False\n'
        'dict2: dict\n'
        "  str: 'value'\n"
        '  list: list\n'
        '    - 1\n'
        '    - 2\n'
        '  bool: False\n'
        'dict3: dict\n'
        "  str: 'value'\n"
        '  list: list\n'
        '    - 1\n'
        '    - 2\n'
        '  bool: False\n'
        'set: set\n'
        '  - 1\n'
        '  - 2\n'
        '  - 3\n'
        'frozenset: set\n'
        '  - 1\n'
        '  - 2\n'
        '  - 3\n'
        'bool: True\n'
        'none: None\n'
        '_private: None\n'
        'repeat: dict\n'
        '  dict: dict\n'
        "    str: 'value'\n"
        '    list: list\n'
        '      - 1\n'
        '      - 2\n'
        '    bool: False\n'
        '    dict: dict\n'
        "      str: 'value'\n"
        '      list: REPEAT\n'
        '      bool: False\n'
        'Empty: Empty\n'
        'Duration: 2d5h\n'
        f'Times: {UNIXMPOCH}')
