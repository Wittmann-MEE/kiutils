from typing import Union


def is_bool_key(item: Union[list, str], key: str) -> bool:
    """
    Checks if `item` represents the given boolean key (e.g. 'power', ['power'], ['power', 'yes']).
    Used to recognize whether a property matches before trying to parse its value.
    Should be called before parse_bool() to avoid misinterpreting other keys.
    """
    if isinstance(item, str):
        return item == key

    if isinstance(item, list) and len(item) >= 1:
        return item[0] == key

    return False


def parse_bool(item: Union[list, str], key: str) -> bool:
    """
    Parse the boolean *value* for a recognized key.
    Assumes is_bool_key(item, key) is True.
    Returns True for implicit or explicit 'yes', False for explicit 'no'.
    """
    if isinstance(item, str) or (isinstance(item, list) and len(item) == 1):
        return True

    if isinstance(item, list) and len(item) == 2:
        return item[1].lower() == "yes"

    raise ValueError(f"Invalid boolean format for key '{key}': {item}")


def format_bool(
    key: str, value: bool, compact: bool = False, yesno: bool = False
) -> list:
    if not isinstance(value, bool):
        raise TypeError(f"Expected a boolean value, got {type(value).__name__}")

    if not yesno and not value:
        return []

    if compact and value:
        return [key]

    if yesno:
        return [key, "yes" if value else "no"]

    return [key, "yes"]
