import decimal

from masoniteorm.query import QueryBuilder


class Tab:
    def __init__(self):
        self.tab_filter_data: dict = {}

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.tab_filter_data.update({"name": name})
        return obj

    def label(self, label: str):
        self.tab_filter_data.update({"label": label})
        return self

    def modify_query_using(self, query: QueryBuilder):
        self.tab_filter_data.update({"query": query})
        return self

    def colspan(self, span: int):
        self.tab_filter_data.update({"colspan": f"{span}"})
        return self

    def icon(self, icon: str):
        self.tab_filter_data.update({"icon": icon})
        return self

    def icon_position(self, position: str):
        self.tab_filter_data.update({"icon_position": position})
        return self

    def badge(self, badge: int | float | decimal.Decimal):
        self.tab_filter_data.update({"badge": badge})
        return self

    def badge_color(self, color: str):
        self.tab_filter_data.update({"badge_color": color})
        return self

    def extra_attributes(self, attributes: dict):
        self.tab_filter_data.update(attributes)
        return self

    def render(self):
        return self.tab_filter_data
