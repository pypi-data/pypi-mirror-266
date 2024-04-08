"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pytest import fixture
from pytest import mark
from pytest import raises

from ..crypts import Crypts
from ..params import CryptsParams



@fixture
def crypts() -> Crypts:
    """
    Construct the instance for use in the downstream tests.

    :returns: Newly constructed instance of related class.
    """

    phrases = {
        'default': Crypts.keygen(),
        'secrets': Crypts.keygen()}

    params = CryptsParams(
        phrases=phrases)

    return Crypts(params=params)



def test_Crypts(
    crypts: Crypts,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param crypts: Primary class instance for the encryption.
    """


    attrs = list(crypts.__dict__)

    assert attrs == [
        '_Crypts__phrases']


    assert repr(crypts)[:23] == (
        '<encommon.crypts.crypts')

    assert hash(crypts) > 0

    assert str(crypts)[:23] == (
        '<encommon.crypts.crypts')


    assert len(crypts.phrases) == 2

    assert len(crypts.keygen()) == 44



@mark.parametrize(
    'value,unique',
    [('foo', 'default'),
     ('foo', 'secrets')])
def test_Crypts_iterate(
    crypts: Crypts,
    value: str,
    unique: str,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param crypts: Primary class instance for the encryption.
    :param value: String value that will returned encrypted.
    :param unique: Unique identifier of mapping passphrase.
    """

    encrypt = (
        crypts.encrypt(value, unique))

    split = encrypt.split(';')

    assert split[1] == '1.0'
    assert split[2] == unique

    decrypt = crypts.decrypt(encrypt)

    assert decrypt == value



def test_Crypts_raises(
    crypts: Crypts,
) -> None:
    """
    Perform various tests associated with relevant routines.

    :param crypts: Primary class instance for the encryption.
    """


    _raises = raises(ValueError)

    with _raises as reason:
        Crypts({'foo': 'bar'})

    _reason = str(reason.value)

    assert _reason == 'default'


    crypts = Crypts(
        crypts.phrases)


    _raises = raises(ValueError)

    with _raises as reason:
        crypts.decrypt('foo')

    _reason = str(reason.value)

    assert _reason == 'string'


    _raises = raises(ValueError)

    with _raises as reason:
        string = '$ENCRYPT;1.1;f;oo'
        crypts.decrypt(string)

    _reason = str(reason.value)

    assert _reason == 'version'
