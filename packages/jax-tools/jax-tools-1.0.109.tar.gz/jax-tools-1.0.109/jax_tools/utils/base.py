# -*- coding:utf-8 -*-
"""
utils base
"""
from typing import TypeVar
import re

KT = TypeVar('KT')
VT = TypeVar('VT')


def sanitize_input(input_string: str) -> str:
    """
    Sanitizes an input string by escaping potentially dangerous characters.

    Args:
        input_string (str): The string to be sanitized.

    Returns:
        str: The sanitized string.
    """

    # 移除或转义特殊字符
    sanitized = re.sub(r'[;|&`\'\"*?~<>^()[\]{}$\\]', '', input_string)
    return sanitized
