from typing import Callable

class Field:
    def __init__(self):
        self.field_data: dict = {}
        self.field_data.update({
            "view": self.view,
        })

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.field_data.update({"name": name})
        return obj

    def class_list(self, classes: list):
        self.field_data.update({"classes": " ".join(classes)})
        return self

    def id(self, id: str):
        self.field_data.update({"id": id})
        return self

    def label(self, label: str):
        self.field_data.update({"label": label})
        return self

    def required(self):
        self.field_data.update({"required": "true"})
        return self

    def disabled(self):
        self.field_data.update({"disabled": "true"})
        return self

    def readonly(self):
        self.field_data.update({"readonly": "true"})
        return self
    
    def autofocus(self):
        self.field_data.update({"autofocus": "true"})
        return self

    def colspan(self, span: str):
        self.field_data.update({"colspan": f"{span}"})
        return self

    def hide_on(self, hide_on: list):
        self.field_data.update({"hide_on": hide_on})
        return self

    def show_on(self, show_on: list):
        self.field_data.update({"show_on": show_on})
        return self

    def mutate(self, func):
        self.field_data.update({"mutate": func})
        return self

    def type(self, type: str):
        self.field_data.update({"type": type})
        return self

    def hidden(self, func: Callable | None = None):
        if func:
            self.field_data.update({"hidden": func})
        else:
            self.field_data.update({"hidden": lambda record: False})
        return self

    def view(self, view_path: str):
        self.field_data.update({"view": view_path})
        return self

    def render(self):
        return self.field_data
    