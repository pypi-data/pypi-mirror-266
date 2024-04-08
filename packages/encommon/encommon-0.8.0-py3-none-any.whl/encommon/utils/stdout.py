"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from dataclasses import dataclass
from re import compile
from re import sub as re_sub
from sys import stdout
from typing import Any
from typing import Literal
from typing import Optional
from typing import Union

from .common import JOINABLE
from ..times import Duration
from ..times import Times
from ..types import Empty
from ..types.strings import COMMAD
from ..types.strings import NEWLINE
from ..types.strings import SEMPTY



ANSICODE = compile(
    r'\x1b\[[^A-Za-z]*[A-Za-z]')

ANSIARRAL = Union[
    list[Any],
    tuple[Any, ...],
    set[Any]]

ANSIARRAD = dict[Any, Any]

ANSIARRAY = Union[
    ANSIARRAL,
    ANSIARRAD]



_REPEAT = (list, tuple, dict)



@dataclass(frozen=True)
class ArrayColors:
    """
    Colors used to colorize the provided array like object.
    """

    label: int = 37
    key: int = 97

    colon: int = 37
    hyphen: int = 37

    bool: int = 93
    none: int = 33
    str: int = 92
    num: int = 93

    times: int = 96
    empty: int = 36
    other: int = 91



def print_ansi(
    string: str = SEMPTY,
    method: Literal['stdout', 'print'] = 'stdout',
    output: bool = True,
) -> str:
    """
    Print the ANSI colorized string to the standard output.

    Example
    -------
    >>> print_ansi('<c91>ERROR<c0>')
    '\\x1b[0;91mERROR\\x1b[0;0m'

    :param string: String processed using inline directives.
    :param method: Which method for standard output is used.
    :param output: Whether or not hte output should be print.
    :returns: ANSI colorized string using inline directives.
    """  # noqa: D301 LIT102

    string = make_ansi(string)

    if output is True:
        if method == 'stdout':
            stdout.write(f'{string}\n')
        else:
            print(string)  # noqa: T201

    return string



def make_ansi(
    string: str,
) -> str:
    """
    Parse the string and replace directives with ANSI codes.

    Example
    -------
    >>> make_ansi('<c91>ERROR<c0>')
    '\\x1b[0;91mERROR\\x1b[0;0m'

    :param string: String containing directives to replace.
    :returns: Provided string with the directives replaced.
    """  # noqa: D301 LIT102

    pattern = r'\<c([\d\;]+)\>'
    replace = r'\033[0;\1m'

    return re_sub(pattern, replace, string)



def kvpair_ansi(
    key: str,
    value: Any,  # noqa: ANN401
) -> str:
    """
    Process and colorize keys and values for standard output.

    Example
    -------
    >>> kvpair_ansi('k', 'v')
    '\\x1b[0;90mk\\x1b[0;37m="\\x1b[0;0m...

    :param key: String value to use for the key name portion.
    :param value: String value to use for the value portion.
    :returns: ANSI colorized string using inline directives.
    """  # noqa: D301 LIT102

    if isinstance(value, JOINABLE):
        value = COMMAD.join([
            str(x) for x in value])

    elif not isinstance(value, str):
        value = str(value)

    return make_ansi(
        f'<c90>{key}<c37>="<c0>'
        f'{value}<c37>"<c0>')



def strip_ansi(
    string: str,
) -> str:
    """
    Return the provided string with the ANSI codes removed.

    Example
    -------
    >>> strip_ansi('\\x1b[0;91mERROR\\x1b[0;0m')
    'ERROR'

    :param string: String which contains ANSI codes to strip.
    :returns: Provided string with the ANSI codes removed.
    """  # noqa: D301 LIT102

    return re_sub(ANSICODE, SEMPTY, string)



def array_ansi(  # noqa: CFQ001, CFQ004
    source: ANSIARRAY,
    *,
    indent: int = 0,
    colors: ArrayColors = ArrayColors(),
) -> str:
    """
    Print the ANSI colorized iterable to the standard output.

    .. note::
       This massive function should be refactored, possibly
       into a class with methods where there are functions.

    Example
    -------
    >>> array_ansi({'foo': 'bar'})
    "\\x1b[0;97mfoo\\x1b[0;37m:\\x1b[0;0m...

    :param source: Value in supported and iterable formats.
    :param indent: How many levels for initial indentation.
    :param colors: Determine colors used with different types.
    :returns: ANSI colorized string using inline directives.
    """  # noqa: D301 LIT102

    output: list[str] = []

    repeat = f'<c{colors.other}>REPEAT<c0>'


    def _append(
        prefix: str,
        value: Any,  # noqa: ANN401
        indent: int,
        refers: set[int],
    ) -> None:

        if id(value) in refers:
            return output.append(
                f'{prefix} {repeat}')


        if isinstance(value, _REPEAT):
            refers.add(id(value))


        typing = {
            'list': list,
            'tuple': tuple,
            'dict': dict,
            'frozenset': frozenset,
            'set': set}

        items = typing.items()

        for name, _type in items:

            if not isinstance(value, _type):
                continue

            output.append(
                f'{prefix} '
                f'<c{colors.label}>'
                f'{name}<c0>')

            return _process(
                source=value,
                indent=indent + 2,
                refers=refers)


        value = _concrete(value)

        output.append(
            f'{prefix} {value}')


    def _concrete(
        source: Any,  # noqa: ANN401
    ) -> str:

        color = colors.other

        if isinstance(source, bool):
            color = colors.bool

        if isinstance(source, int | float):
            color = colors.num

        elif isinstance(source, str):
            color = colors.str

        elif source is None:
            color = colors.none

        elif isinstance(source, Duration):
            color = colors.times

        elif isinstance(source, Times):
            color = colors.times

        elif source is Empty:
            color = colors.empty

        string = f'<c{color}>{source}<c0>'

        if isinstance(source, str):
            string = f"'{string}'"

        return string


    def _dict(
        source: ANSIARRAD,
        indent: int,
        refers: Optional[set[int]] = None,
    ) -> None:

        assert isinstance(source, dict)

        items = source.items()

        for key, value in items:

            prefix = (
                f'{" " * indent}'
                f'<c{colors.key}>{key}'
                f'<c{colors.colon}>:<c0>')

            _append(
                prefix, value, indent,
                refers=refers or set())


    def _list(
        source: ANSIARRAL,
        indent: int,
        refers: Optional[set[int]] = None,
    ) -> None:

        assert isinstance(
            source, (list, tuple, set))

        for value in source:

            prefix = (
                f'{" " * indent}'
                f'<c{colors.hyphen}>-<c0>')

            _append(
                prefix, value, indent,
                refers=refers or set())


    def _process(
        source: ANSIARRAD | ANSIARRAL,
        **kwargs: Any,
    ) -> None:

        if isinstance(source, dict):
            return _dict(source, **kwargs)

        return _list(source, **kwargs)


    if isinstance(source, dict):
        _dict(source, indent)

    elif isinstance(source, list):
        _list(source, indent)

    elif isinstance(source, tuple):
        _list(source, indent)

    elif isinstance(source, set):
        _list(source, indent)


    _output = [
        make_ansi(x) for x in output]

    return NEWLINE.join(_output)
