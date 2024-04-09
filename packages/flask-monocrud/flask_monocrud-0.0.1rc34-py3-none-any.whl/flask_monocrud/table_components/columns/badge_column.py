from .column import Column


class BadgeColumn(Column):
    def __init__(self):
        super().__init__()
        self.column_data.update({"type": "badge"})

    def state_colors(self, pairs: list):
        pairs.append({None: "secondary"})
        self.column_data.update({"state_colors": pairs})
        return self