from typing import Any
import inflection

class HasHeading:
    def get_preview_view_heading(self) -> str:
        pass

    def get_list_view_heading(self) -> str:
        return inflection.pluralize(self.__class__.__name__)

    def get_create_view_heading(self) -> str:
        return f"Create {inflection.singularize(self.__class__.__name__)}"

    def get_edit_view_heading(self) -> str:
        return f"Edit {inflection.singularize(self.__class__.__name__)}"
    