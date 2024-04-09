from flask_monocrud.action_components import Action
from flask_monocrud.form_components import FileUpload, Repeater, TextInput, Select
from flask_monocrud.notification_component import Notification
from flask_monocrud.table_components import BadgeColumn, BooleanColumn, TextColumn
from flask_monocrud.metrics import Metric
from flask_monocrud.table_components.table import Table
from typing import Any
from flask_monocrud.resources.Resource import Resource

class DashboardAdmin(Resource):
    display_in_nav = True  # Display resource in navigation
    menu_icon = ""
    table_polling = False
    table_polling_interval = 5  # seconds

    def get_header_metrics(self):
        return [

        ]


