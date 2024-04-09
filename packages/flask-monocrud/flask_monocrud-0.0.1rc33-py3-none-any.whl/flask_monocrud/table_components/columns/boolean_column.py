from .column import Column


class BooleanColumn(Column):
    def __init__(self):
        super().__init__()
        self.column_data.update({"type": "boolean"})

    def color(self, color):
        self.column_data.update({"color": color})
        return self

    def editable(self):
        self.column_data.update({"editable": True})
        return self