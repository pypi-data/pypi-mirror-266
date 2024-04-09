from pydoc import locate
from typing import Any, List, AnyStr


def to_class(path: str) -> object | None:
    """
    Converts string class path to a Python class.

    Args:
        path (str): The string representing the class path.

    Returns:
        Union[type, None]: The Python class if found, otherwise None.
    """
    try:
        class_instance = locate(path)
    except ImportError:
        print('Module does not exist')
        return None
    return class_instance


def set_attribute(obj: Any, path_string: str, new_value: Any):
    parts: List[AnyStr] = path_string.split('.')
    final_attribute_index: int = len(parts) - 1
    current_attribute = obj
    i: int = 0
    for part in parts:
        new_attr: Any | None = getattr(current_attribute, part, None)
        if current_attribute is None:
            print('Error %s not found in %s' % (part, current_attribute))
            break
        if i == final_attribute_index:
            setattr(current_attribute, part, new_value)
        current_attribute: Any = new_attr
        i += 1


def get_attribute(obj, path_string):
    parts: List[Any] = path_string.split('.')
    final_attribute_index: int = len(parts) - 1
    current_attribute: Any = obj
    i: int = 0
    for part in parts:
        new_attr: Any | None = getattr(current_attribute, part, None)
        if current_attribute is None:
            print('Error %s not found in %s' % (part, current_attribute))
            return None
        if i == final_attribute_index:
            return getattr(current_attribute, part)
        current_attribute: Any = new_attr
        i += 1


def dict_diff_changed_values(dict1, dict2):
    # Find keys that are in both dicts but have different values
    keys_changed = {key for key in dict1.keys() & dict2.keys() if dict1[key] != dict2[key]}

    # Create a new dictionary to store the new values
    diff = {}
    for key in keys_changed:
        diff[key] = dict2[key]

    return diff