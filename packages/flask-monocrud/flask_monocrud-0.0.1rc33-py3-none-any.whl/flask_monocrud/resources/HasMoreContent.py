from typing import Any

class HasMoreContent:
    def before_table_content(self) -> str | tuple[str, dict]:
        return ""

    def after_table_content(self) -> str | tuple[str, dict]:
        return ""
    
    def before_edit_actions_hook(self) -> str:
        return ""
    
    