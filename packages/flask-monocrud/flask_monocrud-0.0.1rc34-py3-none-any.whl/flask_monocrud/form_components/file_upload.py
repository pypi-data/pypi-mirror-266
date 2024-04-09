from . import TextInput

class FileUpload(TextInput):
    view = "admin/components/forms/FileUpload.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "file"})
        self.field_data.update({
            "view": self.view
        })

    def multiple(self):
        self.field_data.update({"multiple": "true"})
        return self

