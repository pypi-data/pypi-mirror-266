from typing import Self

from masoniteorm.collection import Collection

from .text_input import TextInput


class Grid(TextInput):
    view = "admin/components/forms/Grid.html"

    def __init__(self):
        super().__init__()
        self.field_data: dict = {}
        self.field_data.update({
            "view": self.view
        })

        self.field_data.update({"type": "grid"})


    def schema(self, repeater_fields: list):
        """
        :param repeater_fields: The fields to be used for the repeater
        """
        self.field_data.update({"schema": repeater_fields})
        return self


    def cols(self, cols_value: int):
        """
        :param cols_value: The number of columns to be used for the repeater
        """
        self.field_data.update({"cols": cols_value})
        return self
