from .column import Column


class ImageColumn(Column):
    def __init__(self):
        super().__init__()
        self.column_data.update({"type": "image"})

    def path(self, path):
        if "https" in path or "http" in path:
            self.column_data.update({"remote": True})
        self.column_data.update({"local": True})
        self.column_data.update({"path": path})
        return self

    def text(self, id_key):
        self.column_data.update({"text": True})
        self.column_data.update({"id_key": id_key})
        return self

    def boxed(self):
        self.column_data.update({"boxed": True})
        return self

    def circle(self):
        self.column_data.update({"circle": True})
        return self