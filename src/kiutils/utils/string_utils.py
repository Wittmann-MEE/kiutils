"""Functions for string manipulation

Author:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0

Major changes:
    28.02.2022 - created
"""


def dequote(input: str) -> str:
    """Escapes double-quotes in a string using a backslash

    Args:
        - input (str): String to replace double-quotes

    Returns:
        - str: String with replaced double-quotes
    """
    return str(input).replace('"', '\\"')


def quote(s: str) -> str:
    """Wraps a string in double quotes without escaping internal quotes

    Args:
        - s (str): Input string to wrap

    Returns:
        - str: String wrapped in double quotes
    """
    return f'"{s}"'


def escape_and_quote(s: str) -> str:
    """Escapes double-quotes in a string using the external `dequote` function and wraps the result in double quotes

    Args:
        - s (str): Input string to escape and quote

    Returns:
        - str: Escaped string wrapped in double quotes
    """
    return f'"{dequote(s)}"'


def remove_prefix(input: str, prefix: str) -> str:
    """Removes the given prefix from a string (to remove incompatibility of ``str.removeprefix()``
    for Python versions < 3.9)

    Args:
        - input (str): String to remove the prefix from
        - prefix (str): The prefix

    Returns:
        - str: String with removed prefix, or the ``input`` string as is, if the prefix was not found
    """
    return input[len(prefix) :] if input.startswith(prefix) else input
