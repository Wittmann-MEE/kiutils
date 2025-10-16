from typing import Union

def parse_bool(item: Union[list, str], key: str) -> bool:
    """
    Parses a boolean from either old or new format:
    - Old: item is a string like 'hide' or ['hide']
    - New: item is a list like ['hide', 'yes'/'no']
    Returns True if the key matches and the value is "true".
    """
    if isinstance(item, str):
        return item == key
    elif isinstance(item, list) and len(item) == 1:
        return item[0] == key
    elif isinstance(item, list) and len(item) == 2:
        return item[0] == key and item[1].lower() == "yes"

    return False


def format_bool(key: str, value: bool, compact: bool = False, yesno: bool = False) -> str:
    if not isinstance(value, bool):
        raise TypeError(f"Expected a boolean value, got {type(value).__name__}")

    if not yesno and not value:
        return ""

    if compact and value:
        return key

    if yesno:
        return f"({key} {'yes' if value else 'no'})"

    return f"({key} yes)"

def format_bool_raw(key: str, value: bool, compact: bool = False, yesno: bool = False) -> list:
    if not isinstance(value, bool):
        raise TypeError(f"Expected a boolean value, got {type(value).__name__}")

    if not yesno and not value:
        return []

    if compact and value:
        return [key]

    if yesno:
        return [key, 'yes' if value else 'no']

    return [key, 'yes']


