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


def format_bool(key: str, value: bool, compact: bool = False, yesno: bool = False) -> str:
    if not isinstance(value, bool):
        raise TypeError(f"Expected a boolean value, got {type(value).__name__}")
    if not yesno and not value:
        return ""
    else:
        return key if compact else (f"({key} yes)" if not yesno else f"({key} {'yes' if value else 'no'})")

