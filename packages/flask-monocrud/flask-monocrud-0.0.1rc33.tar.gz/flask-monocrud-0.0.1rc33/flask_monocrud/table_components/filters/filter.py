class Filter:
    def __init__(self):
        self.filter_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.filter_data.update({"name": name})
        return obj

    def label(self, label: str):
        self.filter_data.update({"label": label})
        return self

    def default(self, default_filter):
        self.filter_data.update({"default": default_filter})
        return self

    def options(self, options: list):
        self.filter_data.update({"options": options})
        return self

    def id_key(self, id_key: str):
        self.filter_data.update({"id_key": id_key})
        return self

    def value_key(self, value_key: str):
        self.filter_data.update({"value_key": value_key})
        return self

    def relationship(self, relationship: str, column: str):
        self.filter_data.update({"relationship": relationship})
        self.filter_data.update({"column": column})
        return self

    def query(self, query):
        self.filter_data.update({"query": query})
        return self

    def field_type(self, field_type: str):
        self.filter_data.update({"type": field_type})
        return self

    def colspan(self, span: str):
        self.filter_data.update({"colspan": f"{span}"})
        return self

    def render(self):
        return self.filter_data