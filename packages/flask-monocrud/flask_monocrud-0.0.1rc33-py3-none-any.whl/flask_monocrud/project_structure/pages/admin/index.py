from flask_monocrud import Admin
from flask_orphus.routing.fs_router import endpoint



@endpoint(name="Dashboard")
def home():
    return Admin().setup_list_view("Dashboard")

