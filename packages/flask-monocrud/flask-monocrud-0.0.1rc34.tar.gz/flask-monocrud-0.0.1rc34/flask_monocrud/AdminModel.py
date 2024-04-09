from dataclasses import dataclass, field
from typing import Any, Callable, Literal
import urllib.parse

import inflection
from flask_orphus import orequest
from masoniteorm import Model

TTableClickAction = Literal[
    'edit', 'preview'
]

@dataclass
class ResourceNameMutations:
    resource: str = field(default_factory=str)

    def __post_init__(self):
        self.singular = inflection.singularize(self.resource)
        self.plural = inflection.pluralize(self.resource)


@dataclass
class PaginationModel:
    per_page: int = field(default_factory=int)
    page: int = field(default_factory=int)
    total: int = field(default_factory=int)
    per_page_options: list[int] = field(default_factory=list)


@dataclass
class SortModel:
    default: str = field(default_factory=str)
    request_sort: str = field(default_factory=str)
    next_sort: str = field(default_factory=str)


@dataclass
class SearchModel:
    search_field: str | list = field(default_factory=str)
    search_query: str = field(default_factory=str)


@dataclass
class QueryStringModel:
    resource: str = field(default_factory=str)
    model: Model = field(default_factory=Model)

    def __post_init__(self):
        self.query_string = f"/admin/{inflection.pluralize(self.resource).lower()}?" + urllib.parse.urlencode(
            {
                "filter": orequest.input('filter', 'asc'),
                "sort": orequest.input('sort', f'{self.model.get_primary_key()}|desc'),
                "next-sort": ["asc" if orequest.input('sort').split("|")[1] == "desc" else "desc"][
                    0] if orequest.input('sort') else "desc",
                "per_page": orequest.input("per_page", 10),
                "page": orequest.input("page", 1),
                "search_query": orequest.input('search', '%'),
                "toggle_columns": orequest.input('toggle_columns', 'false'),
                **{k: v for k, v in orequest.all().items() if k.startswith("toggle_columns|")},
                **{k: v for k, v in orequest.all().items() if
                   k not in ["filter", "sort", "next-sort", "per_page", "page", "search_query",
                             "toggle_columns"]},
            }, safe='|,=')


@dataclass
class TableModel:
    columns: list[dict[str, Any]] = field(default_factory=list)
    actions: list[dict[str, Any]] = field(default_factory=list)
    bulk_actions: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] | Callable = field(default_factory=list)
    request_filters: str = field(default_factory=str)
    tabs: list[dict[str, Any]] | Callable = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    polling: bool = field(default_factory=bool)
    polling_interval: int = field(default_factory=int)

    search: SearchModel = field(default_factory=SearchModel)
    sort: SortModel = field(default_factory=SortModel)
    query_string: QueryStringModel = field(default_factory=QueryStringModel)

    pagination: PaginationModel = field(default_factory=PaginationModel)

    edit_column: str = field(default_factory=str)
    preview_column: str = field(default_factory=str)

    show_column_borders: bool = field(default_factory=bool)
    table_click_action: TTableClickAction = field(default='preview')


@dataclass
class Hooks:
    before_create: Callable = field(default_factory=Callable)
    after_create: Callable = field(default_factory=Callable)
    before_edit: Callable = field(default_factory=Callable)
    after_edit: Callable = field(default_factory=Callable)
    before_delete: Callable = field(default_factory=Callable)
    after_delete: Callable = field(default_factory=Callable)


@dataclass
class AdminModel:
    resource: str = field(default_factory=str)
    resource_alias: str = field(default_factory=str)
    model: Model = field(default_factory=Model)
    model_instance: Model = field(default_factory=Model)
    name: ResourceNameMutations = field(default_factory=ResourceNameMutations)
    label: str = field(default_factory=str)
    icon: str | bool = field(default_factory=bool)
    table: TableModel = field(default_factory=TableModel)

    display_in_nav: bool = field(default_factory=bool)

    header_metrics: list[dict[str, Any]] = field(default_factory=list)
    fillable: list[dict[str, Any]] = field(default_factory=list)

    models: list[dict[str, Any]] = field(default_factory=list)
    permissions: dict[str, bool] = field(default_factory=dict)

    result_set: Any = field(default_factory=dict)
    hooks: Hooks = field(default_factory=Hooks)

    ignore_during_replication: list[str] = field(default_factory=list)

    def update_result_set(self, result_set: Any):
        self.result_set = result_set
        return self


