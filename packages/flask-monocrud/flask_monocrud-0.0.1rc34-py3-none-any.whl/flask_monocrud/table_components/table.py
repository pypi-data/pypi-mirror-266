class Table:
    def __init__(self):
        self.table_data: dict = {
            "columns": [],
            "filters": [],
            "actions": [],
            "bulk_actions": [],
            "reorderable": False,
            "poll": 0,
        }

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.table_data.update({"name": name})
        return obj

    def columns(self, columns: list):
        self.table_data.update({"columns": columns})
        return self

    def filters(self, filters: list, layout: str = "above"):
        self.table_data.update({"filters": filters})
        return self

    def actions(self, actions: list):
        self.table_data.update({"actions": actions})
        return self


    def bulk_actions(self, bulk_actions: list):
        self.table_data.update({"bulk_actions": bulk_actions})
        return self

    def reorderable(self, value: bool):
        self.table_data.update({"reorderable": value})
        return self

    def poll(self, value: int):
        self.table_data.update({"poll": value})
        return self

    def view(self, value: str):
        self.table_data.update({"view": value})
        return self

    def __dict__(self):
        return self.table_data.get("columns")


