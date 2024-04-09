from flask_monocrud.resources.HasForm import HasForm
from flask_monocrud.resources.HasHeading import HasHeading
from flask_monocrud.resources.HasMetrics import HasMetrics
from flask_monocrud.resources.HasRedirects import HasRedirects
from flask_monocrud.resources.HasTable import HasTable
from flask_monocrud.resources.HasTitle import HasTitle
from flask_monocrud.resources.HasMoreContent import HasMoreContent


class Resource(HasMetrics, HasHeading, HasRedirects, HasForm, HasTable, HasTitle, HasMoreContent):
    navigation_label: str = ""
    display_in_nav: bool = True
    menu_icon: str = ""
    preview_field: str = ""
    edit_field: str = ""
    group: str = ""
    navigation_sort_order: int = 2
    ignore_during_replication: list[str] = []



