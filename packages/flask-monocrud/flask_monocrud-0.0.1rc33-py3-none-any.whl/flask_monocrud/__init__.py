import glob
import inspect
import os

import flask
import inflection
from flask import abort, redirect, render_template, request
from flask_monocrud.AdminModel import AdminModel, ResourceNameMutations, TableModel, SearchModel, \
    SortModel, QueryStringModel, PaginationModel, Hooks
from flask_monocrud.QueryHandler import QueryHandler
from flask_monocrud.ext import FlaskMonoCrud
from flask_monocrud.helpers import getByDot
from flask_monocrud.helpers import to_class
from flask_orphus import orequest
from fuzzywuzzy import process
from masoniteorm import Model
from werkzeug.datastructures.file_storage import FileStorage


def average_of_tuple_index(lst):
    total = 0
    count = 0
    for item in lst:
        total += item[1]
        count += 1
    if count == 0:
        return 0  # Avoid division by zero if the list is empty
    return total / count

def fuzzy_search_list_of_dicts(search_term, data, key) -> int | float:
    # Extract values for the given key from each dictionary
    values = data[key]
    # Perform fuzzy search on the values
    result = process.extract(search_term, values)
    average = average_of_tuple_index(result)
    print(average)
    return average


def returns_empty_list():
    return []


def model_key(model, key, default=None):
    try:
        if type(getByDot(model, key)).__name__ != "method":
            return getByDot(model, key)
        else:
            return getByDot(model, key)()
    except AttributeError:
        return default
    except KeyError:
        return default


class Admin:
    def __init__(self):
        self.admin_object = {}
        self.models = []

    @classmethod
    def make(self, name: str):
        obj = self()
        obj.admin_object.update({"name": name})
        return obj

    def build_table(self, model):
        table = model().get_table()
        return table.__dict__()

    def view(self, view: str):
        self.admin_object.update({"view": view})
        return self

    def build_guards(self, model):
        available_guard_methods = [
            "can_list", "can_view", "can_create", "can_edit", "can_delete", "can_export", "can_import", "can_filter",
            "can_replicate"
        ]
        declared_guards = []

        for method in available_guard_methods:
            if hasattr(model(), method):
                declared_guards.append(method)

        can_list = model().can_list() if "can_list" in declared_guards else True
        can_view = model().can_view() if "can_view" in declared_guards else True
        can_create = model().can_create() if "can_create" in declared_guards else True
        can_edit = model().can_edit() if "can_edit" in declared_guards else True
        can_delete = model().can_delete() if "can_delete" in declared_guards else True
        can_export = model().can_export() if "can_export" in declared_guards else True
        can_import = model().can_import() if "can_import" in declared_guards else True
        can_filter = model().can_filter() if "can_filter" in declared_guards else True
        can_replicate = model().can_replicate() if "can_replicate" in declared_guards else True

        return {
            "can_list": True if can_list is None else can_list,
            "can_view": True if can_view is None else can_view,
            "can_create": True if can_create is None else can_create,
            "can_edit": True if can_edit is None else can_edit,
            "can_delete": True if can_delete is None else can_delete,
            "can_export": True if can_export is None else can_export,
            "can_import": True if can_import is None else can_import,
            "can_filter": True if can_filter is None else can_filter,
            "can_replicate": True if can_replicate is None else can_replicate,
        }

    def hide_table_columns(self, model):
        toggle_columns = {k.replace("toggle_columns|", ""): v for k, v in orequest.all().items() if
                          k.startswith("toggle_columns|")}
        hidden_columns = toggle_columns.keys() if toggle_columns else []
        visible_columns = []
        for column in self.build_table(model):
            if column['name'] not in hidden_columns:
                visible_columns.append(column)
        return visible_columns

    def compile(self, resource, result_set=None):
        model = to_class(f'application.models.{resource}.{resource}')
        admin_model_class = to_class(f'application.admin.{resource}Admin.{resource}Admin')
        admin_model_class_instance = admin_model_class()
        models = self.__generate_models__()
        model_instance = model()  # This allows us to use the model instance to call methods
        admin_model = AdminModel(
            resource=resource,
            resource_alias=getattr(model_instance, "resource_alias", resource),
            model=model,
            model_instance=model_instance,
            name=ResourceNameMutations(resource),
            label=resource,
            icon=False,
            table=TableModel(
                columns=getattr(model_instance, "get_table"),
                actions=getattr(model_instance, "get_table_actions"),
                bulk_actions=getattr(model_instance, "get_table_bulk_actions"),
                filters=getattr(model_instance, "get_table_filters"),
                request_filters=orequest.input('filter', 'asc'),
                tabs=getattr(model_instance, "get_table_tabs"),
                relations=getattr(model_instance, "get_relations"),
                polling=getattr(model_instance, "polling", False),
                polling_interval=getattr(model_instance, "polling_interval", 5),
                search=SearchModel(
                    search_field=getattr(model_instance, "search_field",
                                         getattr(model_instance, "__admin_search_field__", "id")),
                    search_query=orequest.input('search', '%'),
                ),
                sort=SortModel(
                    default=getattr(model_instance, "sort_field",
                                    getattr(model_instance, "__admin_list_filter__", "id")),
                ),
                query_string=QueryStringModel(
                    resource=resource,
                    model=model,
                ),
                pagination=PaginationModel(
                    per_page=orequest.input("per_page", getattr(model_instance, 'per_page')),
                    page=orequest.input("page", 1),
                    per_page_options=getattr(model_instance, 'per_page_options')
                ),
                edit_column=getattr(model_instance, "edit_field", "id"),
                preview_column=getattr(model_instance, "preview_field", "id"),
                show_column_borders=getattr(model_instance, "show_column_borders", False),
                table_click_action=getattr(model_instance, "table_click_action")
            ),
            display_in_nav=getattr(model_instance, "display_in_nav", True),
            ignore_during_replication=getattr(model_instance, "ignore_during_replication"),
            header_metrics=getattr(model_instance, "get_header_metrics", returns_empty_list),
            fillable=getattr(model_instance, "get_fillable", returns_empty_list),
            models=models,
            permissions=self.build_guards(model),
            result_set=result_set,
            hooks=Hooks(
                before_create=getattr(model_instance, "before_create", returns_empty_list),
                after_create=getattr(model_instance, "after_create", returns_empty_list),
                before_edit=getattr(model_instance, "before_edit", returns_empty_list),
                after_edit=getattr(model_instance, "after_edit", returns_empty_list),
                before_delete=getattr(model_instance, "before_delete", returns_empty_list),
                after_delete=getattr(model_instance, "after_delete", returns_empty_list),
            )
        )

        # # add hidden columns to query_params_string
        # for column in self.build_table(admin_model.model):
        #     if column['name'] in orequest.all().keys():
        #         admin_model.table.query_string += f"&toggle_columns|{column['name']}"

        result_set = QueryHandler(
            model_instance, result_set, admin_model
        ).handle().order_by(
            admin_model.table.sort.default, orequest.input("next-sort", "desc")
        )

        result_set = result_set.paginate(
            int(orequest.input("per_page", admin_model.table.pagination.per_page)), int(orequest.input("page", 1))
        )

        admin_model.result_set = result_set or {}

        # if result_set and admin_model.table.search.search_query != "%":
        #     result_set.result = result_set.result.filter(
        #             lambda x: fuzzy_search_list_of_dicts(admin_model.table.search.search_query, x["client"], "Name") == 60.0
        #     )
        #     admin_model.result_set = result_set or {}

        return admin_model

    def setup_list_view(self, resource: str, result_set=None, context=None):
        if context:
            locals().update(**context)

        view_mode = "list"

        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        import timeit
        start_time = timeit.default_timer()
        data_model: AdminModel = self.compile(resource, result_set)
        title = getattr(data_model.model(), "get_list_view_title", lambda: f"{data_model.name.plural.title()}")()

        page_title = getattr(data_model.model(), "get_list_view_heading", lambda: f"{data_model.name.plural.title()}")()
        if data_model.permissions["can_list"] is False:
            return abort(403)

        view = getattr(data_model.model(), "list_view", "admin/views/ListView.html")

        # language=HTML
        if 'hx' not in request.args:
            return render_template(view, **locals())
        else:
            resp = flask.make_response(
                render_template(view, **locals())
            )
            resp.headers['HX-Redirect'] = request.path
            return resp

    def setup_create_view(self, resource: str):
        view_mode = "create"
        data_model = self.compile(resource)
        page_title = getattr(data_model.model(), "get_create_view_heading",
                             lambda: f"Create {data_model.name.singular.title()}")()
        title = getattr(data_model.model(), "get_create_view_title", lambda: f"{data_model.name.singular.title()}")()
        if data_model.permissions.get("can_create") is False:
            return abort(403)
        submit_url = f"/admin/{data_model.name.plural.lower()}/create-{data_model.name.singular.lower()}"
        query_param_string = data_model.table.query_string
        result_set = {}
        fields = data_model.fillable

        view = getattr(data_model.model(), "create_view", "admin/views/CreateView.html")
        return render_template(view, **locals())

    def setup_edit_view(self, resource: str, id: int, result_set=None, context=None):
        if context:
            locals().update(**context)

        view_mode = "edit"

        data_model = self.compile(resource, result_set)
        page_title = getattr(data_model.model(), "get_edit_view_heading",
                             lambda: f"Create {data_model.name.singular.title()}")()
        title = getattr(data_model.model(), "get_edit_view_title", lambda: f"{data_model.name.singular.title()}")()
        model = data_model.model
        edit_field = data_model.table.edit_column
        fields = data_model.fillable
        if data_model.permissions.get("can_edit") is False:
            return abort(403)
        try:
            edit_actions = model().admin_actions()
        except AttributeError:
            edit_actions = None

        try:
            relations = model().get_relations()
        except AttributeError:
            relations = None

        submit_url = f"/admin/{data_model.name.plural.lower()}/{id}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        result_set = model.where(edit_field, id).first()
        if not result_set:
            return abort(404)

        models = data_model.models

        if context:
            if context.get("before_edit_actions_hook", None):
                before_edit_actions_hook = render_template(context["before_edit_actions_hook"], **locals())

        view = getattr(data_model.model(), "edit_view", "admin/views/EditView.html")

        # language=HTML
        return render_template(view, **locals())

    def setup_preview_view(self, resource: str, id: int, result_set=None):
        data_model = self.compile(resource, result_set)
        view_mode = "preview"
        page_title = f"Preview {inflection.singularize(resource).title()}"
        # heading = getattr(data_model.model(), "get_preview_view_heading", lambda: f"Preview {data_model.name.singular.title()}")()

        model: Model | object = data_model.model
        preview_field = data_model.table.preview_column

        if data_model.permissions.get("can_view") is False:
            return abort(403)
        try:
            edit_actions = model().admin_actions()
        except AttributeError:
            edit_actions = None

        try:
            relations = data_model.table.relations
        except AttributeError:
            relations = None

        submit_url = f"/admin/{data_model.name.plural.lower()}/{id}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        result_set = model.where(preview_field, id).first()
        fields = data_model.fillable

        view = getattr(data_model.model(), "preview_view", "admin/views/PreviewView.html")
        # language=HTML
        return render_template(view, **locals())

    def submit_edit_view(self, resource: str, id: int, data):
        data_model = self.compile(resource)
        redirect_url = f"/admin/{data_model.name.plural.lower()}"
        model = data_model.model

        if data_model.permissions.get("can_edit") is False:
            return abort(403)

        save_action = data.get('save-action')
        if save_action == "Save Changes":
            redirect_url = f"/admin/{data_model.name.plural.lower()}"
        elif save_action == "Save & Continue Editing":
            redirect_url = f"/admin/{data_model.name.plural.lower()}/{id}"
        del data['save-action']

        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame

        data_model.update_result_set(model.find(id))

        for key in list(data):
            if type(data[key]).__name__ == FileStorage.__name__:
                del data[key]
                data[key] = orequest.store(key)
        data = data_model.hooks.before_edit(data)
        data_model.result_set.update(data)
        data_model.hooks.after_edit(data_model.result_set)

        if save_action == "Save Changes":
            redirect_url = f"{redirect_url}?hx=true"
            return redirect(redirect_url)
        elif save_action == "Save & Continue Editing":
            redirect_url = f"/admin/{data_model.name.plural.lower()}/{id}"
            return redirect(redirect_url)

    def submit_create_view(self, resource: str, data, redirect_to_new=True):
        data_model = self.compile(resource)
        model = to_class(f'application.models.{resource}.{resource}')
        if data_model.permissions.get("can_create") is False:
            return abort(403)
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame

        save_action = data.get('save-action')
        del data['save-action']

        redirect_url = None
        for key in list(data):
            if type(data[key]).__name__ == FileStorage.__name__:
                del data[key]
                data[key] = orequest.store(key)
            if key == "redirect_url":
                redirect_url = data[key]
                del data[key]

        data = data_model.hooks.before_create(data)
        if isinstance(data, flask.Response):
            data.headers['HX-Redirect'] = data.location
            return data
        new_model = data_model.model.create(data)
        data_model.hooks.after_create(new_model)

        if save_action == "Save & Create New":
            redirect_url = f"/admin/{data_model.name.plural.lower()}/create-{data_model.name.singular.lower()}"
        if save_action == "Save":
            redirect_url = f"/admin/{data_model.name.plural.lower()}"

        if save_action == "Save":
            if redirect_to_new:
                return redirect(f"/admin/{data_model.name.plural.lower()}/{new_model.id}")
            else:
                return redirect(redirect_url)
        elif save_action == "Save & Create New":
            return redirect(redirect_url)

    def delete_view(self, resource: str, id: int):
        data_model = self.compile(resource)
        model = to_class(f'application.models.{resource}.{resource}')
        submit_url = f"/admin/{data_model.name.plural.lower()}"
        inspect.stack()[1][0].f_locals.update(inspect.stack()[0][0].f_locals)  # copy locals from previous frame
        result_set = model.find(id)
        result_set.delete()
        if orequest.has("redirect"):
            return redirect(request.referrer)
        return "", 200

    def __generate_models__(self):
        for file in glob.glob("application/admin" + "/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if name == "__init__":
                continue
            else:
                admin_model = to_class(f"application.admin.{name}.{name}")
                modelname = admin_model.__name__.replace("Admin", "")
                display_in_nav = True
                try:
                    if type(admin_model.display_in_nav) == bool:
                        display_in_nav = admin_model.display_in_nav
                except AttributeError:
                    display_in_nav = True
                if display_in_nav:
                    self.models.append({
                        "name": admin_model.__name__.replace("Admin", ""),
                        "class": to_class(f"application.models.{modelname}.{modelname}"),
                        "label": getattr(admin_model, "navigation_label"),
                        "group": getattr(admin_model, "group"),
                        "navigation_sort_order": getattr(admin_model, "navigation_sort_order", 2),
                    })
        return self.models

    def __register_model__(self, model: str):
        model = {
            "name": model,
            "class": to_class("application.models." + model + "." + model),
            "label": getattr(to_class("application.admin." + model + "Admin." + model + "Admin"), "navigation_label"),
            "group": getattr(to_class("application.admin." + model + "Admin." + model + "Admin"), "group", "unsorted"),
            "navigation_sort": getattr(to_class("application.admin." + model + "Admin." + model + "Admin"),
                                       "navigation_sort_order"),
        }
        self.models.append(model)
        return self

    def __deregiseter_model__(self, model: str):
        self.models = [m for m in self.models if m["name"] != model]
        return self
