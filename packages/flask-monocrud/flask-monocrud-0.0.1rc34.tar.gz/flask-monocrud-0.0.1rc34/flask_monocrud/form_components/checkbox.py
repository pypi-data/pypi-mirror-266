from .field import Field


class Checkbox(Field):
    view = "admin/components/forms/Checkbox.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "checkbox", "checked_color": "primary"})
        self.field_data.update({
            "view": self.view
        })

    def checked(self):
        self.field_data.update({"checked": "true"})
        return self

    def inline(self):
        self.field_data.update({"inline": True})
        return self

    def checked_color(self, color: str):
        self.field_data.update({"checked_color": f"{color}"})
        return self

    def default(self, default: str):
        self.field_data.update({"default": default})
        return self



