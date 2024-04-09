from typing import Self

from masoniteorm.collection import Collection

from .text_input import TextInput


class Repeater(TextInput):
    view = "admin/components/forms/Repeater.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({
            "view": self.view
        })
        self.field_data.update({"type": "repeater", "show_items": False})



    def relationship(self, relationship: Collection) -> Self:
        """
        :param relationship: The relationship to be used for the repeater
        """
        self.field_data.update({"relationship": relationship})
        return self

    def schema(self, repeater_fields: list):
        """
        :param repeater_fields: The fields to be used for the repeater
        """
        self.field_data.update({"schema": repeater_fields})
        return self

    def create_button_label(self, label: str):
        """
        :param label: The label to be used for the create button
        """
        self.field_data.update({"create_button_label": label})
        return self

    def redirect_url(self, url: str):
        """
        :param url: The url to be used for the redirect
        """
        self.field_data.update({"redirect_url": url})
        return self

    def cols(self, cols_value: int):
        """
        :param cols_value: The number of columns to be used for the repeater
        """
        self.field_data.update({"cols": cols_value})
        return self

    def show_items(self, show_items_value: bool):
        """
        :param show_items_value: Determine if repeater records should be shown
        """
        self.field_data.update({"show_items": show_items_value})
        return self


    # Input Types
    def datalist(self, options: list): raise NotImplementedError()
    def date(self): raise NotImplementedError()
    def date_time_local(self): raise NotImplementedError()
    def color(self): raise NotImplementedError()
    def email(self): raise NotImplementedError()
    def month(self): raise NotImplementedError()
    def numeric(self): raise NotImplementedError()
    def password(self): raise NotImplementedError()
    def range(self): raise NotImplementedError()
    def search(self): raise NotImplementedError()
    def tel(self): raise NotImplementedError()
    def time(self): raise NotImplementedError()
    def url(self): raise NotImplementedError()
    def week(self): raise NotImplementedError()
    # CUSTOM ATTRIBUTES
    def max(self, max_value: int): raise NotImplementedError()
    def maxlength(self, maxlength: int): raise NotImplementedError()
    def min(self, min_value: int): raise NotImplementedError()
    def minlength(self, minlength: int): raise NotImplementedError()
    def step(self, step_value: int): raise NotImplementedError()










