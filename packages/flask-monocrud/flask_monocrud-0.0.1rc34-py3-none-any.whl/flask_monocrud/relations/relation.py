class Relation:
    def __init__(self):
        self.relation_data: dict = {
            "can_view": True,
        }

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.relation_data.update({"name": name})
        return obj

    def heading(self, heading: str):
        self.relation_data.update({"heading": heading})
        return self

    def description(self, description: str):
        self.relation_data.update({"description": description})
        return self

    def class_(self, class_name: str):
        self.relation_data.update({"class_": class_name})
        return self

    def model(self, model_name: str):
        self.relation_data.update({"model": model_name})
        return self

    def can_view(self, can_view: bool):
        self.relation_data.update({"can_view": can_view})
        return self


    def render(self):
        if "class_" not in self.relation_data:
            self.relation_data.update({"class_": self.relation_data["model"]})
        return self.relation_data