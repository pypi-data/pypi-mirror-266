from .text_input import TextInput


class Textarea(TextInput):
    view = "admin/components/forms/Textarea.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "textarea"})
        self.field_data.update({
            "view": self.view
        })

    def placeholder(self, placeholder: str):
        self.field_data.update({"placeholder": placeholder})
        return self

    def cols(self, cols_value: int):
        self.field_data.update({"cols": cols_value})
        return self

    def rows(self, rows_value: int):
        self.field_data.update({"rows": rows_value})
        return self

    # Input Types
    def datalist(self, options: list): raise NotImplementedError()
    def date(self): raise NotImplementedError()
    def date_time_local(self): raise NotImplementedError()
    def color(self): raise NotImplementedError()
    def email(self): raise NotImplementedError()
    def month(self): raise NotImplementedError()
    def numeric(self): raise NotImplementedError()
    def password(self): raise NotImplementedError()
    def range(self): raise NotImplementedError()
    def search(self): raise NotImplementedError()
    def tel(self): raise NotImplementedError()
    def time(self): raise NotImplementedError()
    def url(self): raise NotImplementedError()
    def week(self): raise NotImplementedError()
    # CUSTOM ATTRIBUTES
    def max(self, max_value: int): raise NotImplementedError()
    def maxlength(self, maxlength: int): raise NotImplementedError()
    def min(self, min_value: int): raise NotImplementedError()
    def minlength(self, minlength: int): raise NotImplementedError()
    def step(self, step_value: int): raise NotImplementedError()










