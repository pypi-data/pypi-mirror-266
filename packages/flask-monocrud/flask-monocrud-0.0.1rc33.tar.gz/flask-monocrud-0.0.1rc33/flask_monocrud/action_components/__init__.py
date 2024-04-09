from flask import render_template
from typing import Callable

class Action:
    def __init__(self):
        self.action_data: dict = {}
        self.action_data.update({"hidden": lambda record: True})

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.action_data.update({"name": name, "type": "action"})
        return obj

    def label(self, label: str):
        self.action_data.update({"label": label})
        return self

    def action(self, action):
        self.action_data.update({"action": action})
        return self

    def view(self, view: str):
        view = render_template(f"components/actions/{view}.html")
        self.action_data.update({"view": view})
        return self

    def color(self, color: str):
        self.action_data.update({"color": color})
        return self

    def redirect_url(self, url: str):
        self.action_data.update({"redirect_url": url})
        return self

    def schema(self, action_fields: list):
        self.action_data.update({"schema": action_fields})
        return self

    def html(self, html: str):
        self.action_data.update({"html": html})
        return self

    def hidden(self, func: Callable):
        self.action_data.update({"hidden": func})
        return self

    def context(self, context: dict):
        self.action_data.update({"context": context})
        return self

    def size(self, size: str="sm"):
        if size.lower() not in ["sm", "md", "lg", "xl"]:
            raise Exception(f"Invalid size[{size.lower()}] for action {self.action_data.get('name')}. Must be one of sm, md, lg, xl")
        self.action_data.update({"size": size})
        return self

    def hide_footer(self, hide_footer: bool):
        self.action_data.update({"hide_footer": hide_footer})
        return self

    def render(self):
        return self.action_data
    