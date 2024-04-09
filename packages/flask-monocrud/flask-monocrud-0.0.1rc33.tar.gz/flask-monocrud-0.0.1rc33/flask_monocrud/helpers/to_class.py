from pydoc import locate
from typing import Any


def to_class(path: str) -> Any:
    """
        Converts string class path to a python class

    return:
        mixed
    """
    try:
        class_instance = locate(path)
    except ImportError:
        print('Module does not exist')
    return class_instance or None