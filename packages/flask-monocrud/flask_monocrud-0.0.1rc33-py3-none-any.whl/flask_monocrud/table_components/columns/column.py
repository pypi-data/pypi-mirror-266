from flask_monocrud.helpers.get_type import get_type
from typing import Callable

class Column:
    def __init__(self):
        self.column_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.column_data.update({"name": name})
        return obj

    def label(self, label: str | Callable):
        if get_type(label) != "str":
            raise TypeError(f"Label must be a string not [{get_type(label)}].")
        self.column_data.update({"label": label})
        return self

    def default(self, value: str):
        self.column_data.update({"default": value})
        return self

    def sortable(self):
        self.column_data.update({"sortable": True})
        return self

    def filterable(self):
        self.column_data.update({"filterable": True})
        return self

    def editable(self):
        raise NotImplementedError("Editable table columns are not implemented as yet. Will be available in a future release.")
        self.column_data.update({"editable": True})
        return self

    def hidden(self):
        self.column_data.update({"hidden": True})
        return self

    def mutate(self, func):
        self.column_data.update({"mutate": func})
        return self

    def render(self):
        return self.column_data

