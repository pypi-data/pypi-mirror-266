from . import Checkbox

class Radio(Checkbox):
    view = "admin/components/forms/Radio.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({"type": "radio", "checked_color": "primary"})
        self.field_data.update({
            "view": self.view
        })




