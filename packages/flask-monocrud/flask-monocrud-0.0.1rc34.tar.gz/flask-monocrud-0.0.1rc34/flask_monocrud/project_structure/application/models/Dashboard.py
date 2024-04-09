from masoniteorm.models import Model
from application.admin.DashboardAdmin import DashboardAdmin
from application.policies.DashboardPolicies import DashboardPolicies
from application.hooks.DashboardHooks import DashboardHooks


class Dashboard(Model, DashboardAdmin, DashboardPolicies, DashboardHooks):
    __guarded__ = ["csrf_token"]

