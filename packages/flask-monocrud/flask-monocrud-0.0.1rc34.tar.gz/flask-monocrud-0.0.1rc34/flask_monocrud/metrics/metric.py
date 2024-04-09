class Metric:
    def __init__(self):
        self.metric_data: dict = {}
        self.metric_data.update({
            "colspan": "2",
        })

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.metric_data.update({"name": name})
        return obj

    def heading(self, heading: str):
        self.metric_data.update({"heading": heading})
        return self

    def description(self, description: str):
        self.metric_data.update({"description": description})
        return self

    def icon(self, icon: str):
        self.metric_data.update({"icon": icon})
        return self

    def icon_color(self, icon_color: str):
        self.metric_data.update({"icon_color": icon_color})
        return self

    def icon_bg_color(self, icon_bg_color: str):
        self.metric_data.update({"icon_bg_color": icon_bg_color})
        return self

    def color(self, color: str):
        self.metric_data.update({"color": color})
        return self

    def value(self, value: str, prefix=None, suffix=None):
        self.metric_data.update({"value": f"{prefix or ''}{value}{suffix or ''}"})
        return self

    def colspan(self, span: str):
        self.metric_data.update({"colspan": f"{span}"})
        return self

    def render(self):
        return self.metric_data
