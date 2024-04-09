from . field import Field

class Select(Field):
    view = "admin/components/forms/Select.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "select", "id_key": "id", "value_key": "name"})
        self.field_data.update({
            "view": self.view
        })

    def options(self, options: list):
        self.field_data.update({"options": options})
        return self

    def label(self, label: str):
        self.field_data.update({"label": label})
        return self

    def id_key(self, id_key: str):
        self.field_data.update({"id_key": id_key})
        return self

    def value_key(self, value_key: str):
        self.field_data.update({"value_key": value_key})
        return self

    def selected(self):
        self.field_data.update({
            "selected": "selected"
        })
        return self
