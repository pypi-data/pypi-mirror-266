"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from ..hashes import Hashes



def test_Hashes() -> None:
    """
    Perform various tests associated with relevant routines.
    """

    hashes = Hashes('string')

    attrs = list(hashes.__dict__)

    assert attrs == [
        '_Hashes__string']


    assert repr(hashes).startswith(
        '<encommon.crypts.hashes.Hashes')
    assert isinstance(hash(hashes), int)
    assert str(hashes).startswith(
        '<encommon.crypts.hashes.Hashes')


    assert hashes.string == 'string'


    assert hashes.md5.startswith('b4')
    assert hashes.md5.endswith('0f21')

    assert hashes.sha1.startswith('ec')
    assert hashes.sha1.endswith('904d')

    assert hashes.sha256.startswith('47')
    assert hashes.sha256.endswith('2fa8')

    assert hashes.sha512.startswith('27')
    assert hashes.sha512.endswith('6a87')

    assert hashes.uuid.startswith('38')
    assert hashes.uuid.endswith('eee4')

    assert hashes.apache.startswith('7L')
    assert hashes.apache.endswith('kE0=')
