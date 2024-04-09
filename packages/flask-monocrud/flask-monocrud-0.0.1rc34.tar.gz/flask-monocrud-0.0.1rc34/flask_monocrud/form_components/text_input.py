from .field import Field
from typing import Callable


class TextInput(Field):
    view = "admin/components/forms/TextInput.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "text"})
        self.field_data.update({
            "view": self.view
        })

    def default(self, default: str):
        self.field_data.update({"default": default})
        return self

    def disable_autocomplete(self):
        self.field_data.update({"autocomplete": "off"})
        return self

    # Input Types
    def datalist(self, options: list):
        self.field_data.update({"type": "datalist", "options": options})
        return self

    def date(self):
        self.field_data.update({"type": "date"})
        return self

    def date_time_local(self):
        self.field_data.update({"type": "datetime-local"})
        return self

    def color(self):
        self.field_data.update({"type": "color"})
        return self

    def email(self):
        self.field_data.update({"type": "email"})
        return self

    def month(self):
        self.field_data.update({"type": "month"})
        return self

    def numeric(self):
        self.field_data.update({"type": "number"})
        return self

    def password(self):
        self.field_data.update({"type": "password"})
        return self

    def range(self):
        self.field_data.update({"type": "range"})
        return self

    def search(self):
        self.field_data.update({"type": "search"})
        return self

    def tel(self):
        self.field_data.update({"type": "tel"})
        return self

    def time(self):
        self.field_data.update({"type": "time"})
        return self

    def url(self):
        self.field_data.update({"type": "url"})
        return self

    def week(self):
        self.field_data.update({"type": "week"})
        return self

    def year(self):
        self.field_data.update({"type": "year"})
        return self


    def placeholder(self, placeholder: str):
        self.field_data.update({"placeholder": placeholder})
        return self


    # CUSTOM ATTRIBUTES
    def max(self, max_value: int):
        self.field_data.update({"max": f"{max_value}"})
        return self

    def maxlength(self, maxlength: int):
        if type(maxlength) == int:
            self.field_data.update({"maxlength": f"{maxlength}"})
            return self
        raise TypeError("maxlength must be an integer")

    def min(self, min_value: int):
        self.field_data.update({"min": f"{min_value}"})
        return self

    def minlength(self, minlength: int):
        if type(minlength) == int:
            self.field_data.update({"minlength": f"{minlength}"})
            return self
        raise TypeError("minlength must be an integer")

    def step(self, step_value: int):
        self.field_data.update({"step": f"{step_value}"})
        return self





