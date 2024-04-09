from . import Checkbox

class Toggle(Checkbox):
    view = "admin/components/forms/Toggle.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({
            "type": "toggle",
            "checked_color": "primary",
        })
        self.field_data.update({
            "view": self.view
        })






