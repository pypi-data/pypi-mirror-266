class HorizontalSeparator:
    def __init__(self):
        self.field_data: dict = {}
        self.field_data.update({
            "view": "admin/components/forms/HorizontalSeparator.html",
            "type": "horizontal-separator"
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

    def view(self, view_path: str):
        self.field_data.update({"view": view_path})
        return self

    def render(self):
        return self.field_data