from typing import Any

class HasForm:
    def get_fillable(self) -> list[dict[str, Any]]:
        return []