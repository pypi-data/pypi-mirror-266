"""
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
"""



from pydantic import BaseModel



class CryptsParams(BaseModel, extra='forbid'):
    """
    Process and validate the common configuration parameters.

    :param phrases: Passphrases that are used in operations.
    :param data: Keyword arguments passed to Pydantic model.
        Parameter is picked up by autodoc, please ignore.
    """

    phrases: dict[str, str]
