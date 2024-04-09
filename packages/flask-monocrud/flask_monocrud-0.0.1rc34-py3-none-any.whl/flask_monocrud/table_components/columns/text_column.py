from .column import Column


class TextColumn(Column):
    def __init__(self):
        super().__init__()
        self.column_data.update({"type": "text"})

    def description(self, description: str):
        self.column_data.update({"description": description})
        return self

    def datetime(self, in_fmt: str, out_fmt: str):
        self.column_data.update({"datetime": True, "in_fmt": in_fmt, "out_fmt": out_fmt})
        return self

    def money(self, currency: str):
        self.column_data.update({"money": currency})
        return self

    def limit(self, limit: int):
        self.column_data.update({"limit": limit})
        return self

    def words(self, words: int):
        self.column_data.update({"words": words})
        return self

    def html(self):
        self.column_data.update({"html": True})
        return self

    def placeholder(self, placeholder: str):
        self.column_data.update({"placeholder": placeholder})
        return self

    # Column Header Options
    def sortable(self):
        self.column_data.update({"sortable": True})
        return self



