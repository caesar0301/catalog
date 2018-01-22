"""
Typed environment variables.
Published by Va1 under Apache License 2.0.
https://github.com/Va1/smart-getenv
"""

import os
from ast import literal_eval


__version__ = '1.1.0'


def getenv(name, **kwargs):
    """
    Retrieves environment variable by name and casts the value to desired type.
    If desired type is list or tuple - uses separator to split the value.
    """
    default_value = kwargs.pop('default', None)
    desired_type = kwargs.pop('type', str)
    list_separator = kwargs.pop('separator', ',')

    value = os.getenv(name, None)

    if value is None:
        if default_value is None:
            return None
        else:
            return default_value

    if desired_type is bool:
        if value.lower() in ['false', '0']:
            return False
        else:
            return bool(value)

    if desired_type is list or desired_type is tuple:
        value = value.split(list_separator)
        return desired_type(value)

    if desired_type is dict:
        return dict(literal_eval(value))

    return desired_type(value)