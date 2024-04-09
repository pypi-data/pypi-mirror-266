from typing import Any
from flask_monocrud.AdminModel import TTableClickAction


class HasTable:
    table_polling: bool = False
    table_polling_interval: int = 5
    show_column_borders: bool = False
    table_click_action: TTableClickAction = 'preview'
    per_page_options: list[int] = [5, 15, 25, 50, 75, 100]
    per_page: int = 10
    search_field: str | list[str] = "id"

    def get_table(self) -> list[dict[str, Any]]:
        return []

    def get_relations(self) -> list[dict[str, Any]]:
        return []

    def get_table_actions(self) -> list[dict[str, Any]]:
        return []

    def get_table_filters(self) -> list[dict[str, Any]]:
        return []

    def get_table_tabs(self) -> list[dict[str, Any]]:
        return []

    def get_table_bulk_actions(self) -> list[dict[str, Any]]:
        return []