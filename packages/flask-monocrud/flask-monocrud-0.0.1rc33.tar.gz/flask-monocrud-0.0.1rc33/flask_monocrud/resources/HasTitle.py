from typing import Any

import inflection
from flask_monocrud.helpers import from_config

class HasTitle:
    def get_list_view_title(self) -> str:
        return f'{from_config("admin.admin_title_prefix")} {inflection.pluralize(self.__class__.__name__)} {from_config("admin.admin_title_suffix")}'

    def get_edit_view_title(self) -> str:
        return f'{from_config("admin.admin_title_prefix")} Edit {inflection.singularize(self.__class__.__name__)} {from_config("admin.admin_title_suffix")}'

    def get_create_view_title(self) -> str:
        return f'{from_config("admin.admin_title_prefix")} Create {inflection.singularize(self.__class__.__name__)} {from_config("admin.admin_title_suffix")}'