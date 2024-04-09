from flask import render_template_string
from packages.experimental.Hubi.Hubi import render


class Reactive:
    def __init__(self):
        self.component_data: dict = {}

    @classmethod
    def make(self, name: str, key=""):
        obj = self()
        obj.component_data.update({"type": "live", "name": name})
        return obj

    def render(self):
        return self.component_data
