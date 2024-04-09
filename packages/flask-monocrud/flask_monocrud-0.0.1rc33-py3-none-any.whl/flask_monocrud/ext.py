import datetime
import inspect
import os
import pprint
import shutil

import click
import inflection
import jinja2
import markupsafe
import werkzeug
import yaml
from flask import render_template, request, g, render_template_string
from flask_orphus.routing.fs_router import FSRouter
from flask_wtf import CSRFProtect
from masoniteorm.query import QueryBuilder
from orjson import orjson

from flask_monocrud.flask_debugtoolbar import DebugToolbarExtension, module
from flask_monocrud.helpers import to_class, copy_folder_contents
from flask_monocrud.project_structure.application.traits.EnhancedModelTrait import EnhancedModelTrait


def find_all_subclasses(class_type):
    subclasses = set()
    work = [class_type]
    print(class_type)
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def get_current_record(self):
    builder = self.__dict__['__dirty_attributes__']['builder']
    return builder.first()


def FlaskMonoCrud(app, secret_key=os.urandom(24)):
    setattr(QueryBuilder, 'with_where_has', EnhancedModelTrait.with_where_has)
    setattr(QueryBuilder, "where_any", EnhancedModelTrait.where_any)

    class SingletonObject:
        def __init__(self):
            self.data = None
            self.queries = []

    # Create a function to get or create the singleton object
    def get_singleton_object():
        if not hasattr(g, 'singleton_object'):
            g.singleton_object = SingletonObject()
        return g.singleton_object

    package_dir = os.path.dirname(os.path.abspath(__file__))

    loader = jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.FileSystemLoader(os.path.join(package_dir, "templates")),
        ]
    )
    app.jinja_env.loader = loader
    app.jinja_options["undefined"] = jinja2.ChainableUndefined
    FSRouter(app)
    app.secret_key = secret_key
    csrf = CSRFProtect(app)
    csrf.exempt(module)
    # DebugToolbarExtension(app)
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # app.config['SQLALCHEMY_RECORD_QUERIES'] = True

    # @app.errorhandler(Exception)
    # def forbidden(e):
    #     error = {
    #         "title": f"{str(e).split(':')[0]}",
    #         "message": e,
    #     }
    #     return render_template('components/layouts/DefaultErrorPage.html', error=error), 403

    def getByDot(obj, ref):
        """
        Use MongoDB style 'something.by.dot' syntax to retrieve objects from Python dicts.

        This also accepts nested arrays, and accommodates the '.XX' syntax that variety.js
        produces.

        Usage:
           >>> x = {"top": {"middle" : {"nested": "value"}}}
           >>> q = 'top.middle.nested'
           >>> getByDot(x,q)
           "value"
        """
        val = obj
        tmp = ref
        ref = tmp.replace(".XX", "[0]")
        if tmp != ref:
            print("Warning: replaced '.XX' with [0]-th index")
        for key in ref.split('.'):
            idstart = key.find("[")
            embedslist = 1 if idstart > 0 else 0
            if embedslist:
                idx = int(key[idstart + 1:key.find("]")])
                kyx = key[:idstart]
                try:
                    val = val[kyx][idx]
                except IndexError:
                    print("Index: x['{}'][{}] does not exist.".format(kyx, idx))
                    raise
            else:
                if val:
                    try:
                        val = val[key]
                    except TypeError:
                        if get_type(val) == "bytes":
                            val = orjson.loads(val)[key]
                            return (val)
                        try:
                            val = val()[key]
                        except TypeError as e:
                            if "'Collection' object is not callable" in str(e):
                                val = val.first()[key]
                        # raise TypeError("TypeError: val[{}]".format(key))
                else:
                    val = None
        return (val)

    @app.template_global()
    def from_config(key):
        config = yaml.load(open("config/config.yaml", "r"), Loader=yaml.FullLoader)
        return getByDot(config, key)

    @app.template_global()
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

    @app.template_global()
    def get_class(name, directory="models"):
        if directory == "models":
            return to_class(f'application.{directory}.{name}.{name}')
        elif directory == "admin":
            name = singularize(name)
            # raise Exception(find_all_subclasses(to_class(f'application.{directory}.{name}Admin.{name}Admin')))
            # raise Exception(to_class(f'application.{directory}.{name}Admin.{name}Admin').__dict__)
            return to_class(f'application.{directory}.{name}Admin.{name}Admin')()
        else:
            return to_class(f'application.{directory}.{name}.{name}')

    @app.template_global()
    def get_type(value):
        return type(value).__name__

    @app.template_global()
    def titleize(name: str) -> str:
        return inflection.titleize(name)

    @app.template_global()
    def pluralize(name: str) -> str:
        return inflection.pluralize(name)

    @app.template_global()
    def singularize(name: str) -> str:
        return inflection.singularize(name)

    @app.template_global()
    def humanize(name: str) -> str:
        return inflection.humanize(name)

    @app.template_global()
    def markup(html):
        return markupsafe.Markup(html)

    @app.template_global()
    def find_key_in_dict(list_of_dicts, key, value):
        for item in list_of_dicts:
            if item[key] == value:
                return item

    @app.template_global()
    def currency_fmt(fmt, value):
        from currencies import Currency
        currency = Currency(fmt.upper())
        return currency.get_money_format(value)

    @app.template_global()
    def datetime_fmt(fmt_in, fmt_out, value):
        return datetime.datetime.strptime(value, fmt_in).strftime(fmt_out)

    @app.template_global()
    def limit_words(limit, value):
        import re
        words = re.findall(r'\w+', value)[:limit]
        limited_value = " ".join(words)
        return limited_value

    @app.template_global()
    def get_file_internal(directory, image):
        from flask import send_from_directory
        import base64
        try:
            response = send_from_directory(directory, image, as_attachment=False)
            with open(f"{directory}/{image}", "rb") as f:
                extracted_bytes = f.read()
            uri = (
                f"data:{response.headers['Content-Type']};base64,{base64.b64encode(extracted_bytes).decode('utf-8')}")
            return uri
        except werkzeug.exceptions.NotFound:
            return None

    @app.template_global()
    def inject_template_hook(hook_name):
        return '''
            {% if model_key(data_model.model, 'TEMPLATE_HOOK_PLACEHOLDER') %}
                {% set tmpl_with_context = model_key(data_model.model, 'TEMPLATE_HOOK_PLACEHOLDER') %}
                {% set tmpl = tmpl_with_context[0] %}
                {% set ctx = tmpl_with_context[1] %}
                {{ render_dynamic_html(tmpl, **ctx) }}
            {% endif %}
        '''.replace("TEMPLATE_HOOK_PLACEHOLDER", hook_name)

    @app.template_global()
    def render_dynamic_html(html, **kwargs):
        from flask_orphus.routing.micro import micro_render
        from flask import current_app
        return render_template_string(html, **inspect.stack()[0][0].f_locals['kwargs'])

    @app.template_global()
    def is_debug():
        return app.debug

    @app.cli.command("create-monocrud")
    def create_monocrud():
        # get directory of this file
        package_dir = os.path.dirname(os.path.abspath(__file__))
        project_structure_dir = os.path.join(package_dir, "project_structure")
        project_dir = os.getcwd()
        os.system(f"xcopy {project_structure_dir} {project_dir} /E /Y")

    @app.cli.command("create-resource")
    @click.argument("resource")
    def create_resource(resource: str):
        package_dir = os.path.dirname(os.path.abspath(__file__))
        stubs_dir = os.path.join(package_dir, "stubs")
        resource = inflection.singularize(resource).title()
        from string import Template
        create_view = Template(open(os.path.join(stubs_dir, "create-view.stub"), "r").read()).substitute(
            Resource=resource)
        edit_view = Template(open(os.path.join(stubs_dir, "edit-view.stub"), "r").read()).substitute(
            Resource=resource)
        preview_view = Template(open(os.path.join(stubs_dir, "preview-view.stub"), "r").read()).substitute(
            Resource=resource)
        list_view = Template(open(os.path.join(stubs_dir, "list-view.stub"), "r").read()).substitute(
            Resource=resource)
        submit_create = Template(open(os.path.join(stubs_dir, "submit-create.stub"), "r").read()).substitute(
            Resource=resource)
        submit_edit = Template(open(os.path.join(stubs_dir, "submit-edit.stub"), "r").read()).substitute(
            Resource=resource)
        submit_delete = Template(open(os.path.join(stubs_dir, "submit-delete.stub"), "r").read()).substitute(
            Resource=resource)
        resource_admin = Template(open(os.path.join(stubs_dir, "resource-admin.stub"), "r").read()).substitute(
            Resource=resource, ResourceAdmin=resource + "Admin")
        resource_policies = Template(open(os.path.join(stubs_dir, "resource-policies.stub"), "r").read()).substitute(
            Resource=resource, ResourcePolicies=resource + "Policies")
        resource_hooks = Template(open(os.path.join(stubs_dir, "resource-hooks.stub"), "r").read()).substitute(
            Resource=resource, ResourceHooks=resource + "Hooks")
        resource_model = Template(open(os.path.join(stubs_dir, "resource-model.stub"), "r").read()).substitute(
            Resource=resource, ResourceAdmin=resource + "Admin", ResourcePolicies=resource + "Policies",
            ResourceHooks=resource + "Hooks")
        migration_file = open(os.path.join(stubs_dir, "migration.stub"), "r").read().replace(
            "__MIGRATION_NAME__", f"Create{inflection.pluralize(resource)}Migration").replace(
            "__ResourceLower__", inflection.pluralize(resource).lower()
        )

        project_dir = os.getcwd()
        admin_pages_dir = os.path.join(os.getcwd(), "pages", "admin")
        models_dir = os.path.join(os.getcwd(), "application", "models")
        admin_dir = os.path.join(os.getcwd(), "application", "admin")
        policies_dir = os.path.join(os.getcwd(), "application", "policies")
        hooks_dir = os.path.join(os.getcwd(), "application", "hooks")
        migration_dir = os.path.join(os.getcwd(), "databases", "migrations")

        new_resource_dir = os.path.join(admin_pages_dir, inflection.pluralize(resource).lower())
        try:
            os.mkdir(new_resource_dir)
        except FileExistsError:
            print("Directory already exists")

        create_view_path = os.path.join(new_resource_dir, "create-" + resource.lower() + ".py")
        edit_view_path = os.path.join(new_resource_dir, "[id]" + ".py")
        preview_view_path = os.path.join(new_resource_dir, "[id]~preview" + ".py")
        list_view_path = os.path.join(new_resource_dir, "index" + ".py")
        submit_create_path = os.path.join(new_resource_dir, "create-" + resource.lower() + "(post)" + ".py")
        submit_edit_path = os.path.join(new_resource_dir, "[id]" + "(post)" + ".py")
        submit_delete_path = os.path.join(new_resource_dir, "[id]" + "delete" + ".py")

        resource_admin_path = os.path.join(admin_dir, resource + "Admin.py")
        resource_policies_path = os.path.join(policies_dir, resource + "Policies.py")
        resource_hooks_path = os.path.join(hooks_dir, resource + "Hooks.py")
        resource_model_path = os.path.join(models_dir, resource + ".py")

        paths_to_create = [
            {"path": create_view_path, "content": create_view},
            {"path": edit_view_path, "content": edit_view},
            {"path": preview_view_path, "content": preview_view},
            {"path": list_view_path, "content": list_view},
            {"path": submit_create_path, "content": submit_create},
            {"path": submit_edit_path, "content": submit_edit},
            {"path": submit_delete_path, "content": submit_delete},
            {"path": resource_admin_path, "content": resource_admin},
            {"path": resource_model_path, "content": resource_model},
            {"path": resource_policies_path, "content": resource_policies},
            {"path": resource_hooks_path, "content": resource_hooks},
        ]

        for path in paths_to_create:
            if not os.path.exists(path["path"]):
                open(path["path"], "w").write(path["content"])
            else:
                print(f"File {path['path']} already exists")

        dt_obj_str = str(datetime.datetime.now()).replace("-", "_")
        date = dt_obj_str.split(" ")[0]
        time = dt_obj_str.split(" ")[1].split(".")[0].replace(":", "")

        os.system(
            f"masonite-orm migration create_{inflection.pluralize(resource).lower()}_table --create {inflection.pluralize(resource).lower()}")

        print("Successfully created resource " + resource + "!")
        print("The following files were created:")
        print(f""
              f"{list_view_path}\n"
              f"{edit_view_path}\n"
              f"{preview_view_path}\n"
              f"{submit_edit_path}\n"
              f"{create_view_path}\n"
              f"{submit_create_path}\n"
              f"{resource_model_path}\n"
              f"{resource_policies_path}\n"
              f"{resource_hooks_path}\n"
              f"{resource_admin_path}\n")

    @app.cli.command("migration")
    @click.argument("migration")
    def migration(migration: str):
        os.system(f"masonite-orm migration {migration}")

    @app.cli.command("migrate")
    def migrate():
        os.system(f"masonite-orm migrate")

    @app.cli.command("seed")
    def seed():
        os.system(f"masonite-orm seed")

    @app.cli.command("rollback")
    def rollback():
        os.system(f"masonite-orm rollback")

    @app.cli.command("refresh")
    def refresh():
        os.system(f"masonite-orm refresh")

    @app.cli.command("reset")
    def reset():
        os.system(f"masonite-orm reset")
