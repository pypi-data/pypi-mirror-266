"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from base64 import b64encode
from hashlib import md5
from hashlib import sha1
from hashlib import sha256
from hashlib import sha512
from uuid import NAMESPACE_DNS
from uuid import uuid3



class Hashes:
    """
    Create hash values using the provided at instantiation.

    Example
    -------
    >>> hashes = Hashes('string')
    >>> hashes.sha256
    '473287f8298dba7163a897908958f7c0ea...

    Example
    -------
    >>> hashes = Hashes('string')
    >>> hashes.uuid
    '38ffd1ed-2b4d-3c84-ae45-bf3bf354eee4'

    :param string: String which will be used within hashing.
    """

    __string: str


    def __init__(
        self,
        string: str,
    ) -> None:
        """
        Initialize instance for class using provided parameters.
        """

        self.__string = string


    @property
    def string(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        return self.__string


    @property
    def md5(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        encode = self.__string.encode()

        return md5(encode).hexdigest()


    @property
    def sha1(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        string = self.__string.encode()

        return sha1(string).hexdigest()


    @property
    def sha256(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        string = self.__string.encode()

        return sha256(string).hexdigest()


    @property
    def sha512(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        string = self.__string.encode()

        return sha512(string).hexdigest()


    @property
    def uuid(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        string = self.__string

        return str(
            uuid3(NAMESPACE_DNS, string))


    @property
    def apache(
        self,
    ) -> str:
        """
        Return the value for the attribute from class instance.

        :returns: Value for the attribute from class instance.
        """

        string = self.__string.encode()

        digest = sha1(string).digest()

        return b64encode(digest).decode()
