import os.path
from typing import Any


def check_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def ensure_dir_exists(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def ensure_parent_dir_exists(path: str) -> None:
    ensure_dir_exists(os.path.dirname(path))


def bytes_to_hex(value: str | bytes) -> str:
    """
    Converts a string or bytes object to its hexadecimal representation.

    If the input is already a string, it assumes that the string is already in
    hexadecimal format and returns it as is. If the input is bytes, it converts
    the bytes to their hexadecimal string representation.

    Args:
        x: The input string or bytes object to be converted to hexadecimal.

    Returns:
        The hexadecimal representation of the input.

    Examples:
        _to_hex(b'hello') returns '68656c6c6f'
        _to_hex('68656c6c6f') returns '68656c6c6f'
    """
    if isinstance(value, bytes):
        return value.hex()
    assert isinstance(value, str)
    # TODO: Check that `value` is a valid hexadecimal string
    return value
