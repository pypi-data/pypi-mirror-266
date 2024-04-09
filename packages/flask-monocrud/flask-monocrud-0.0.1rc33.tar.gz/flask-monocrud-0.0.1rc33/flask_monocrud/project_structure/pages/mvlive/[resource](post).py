import json
import pprint
from typing import Dict, Any, Optional

from MVLive import MVLive
from flask import request, Response, url_for, redirect, flash

from mvlive.utils import to_class
from flask_orphus.routing.fs_router import endpoint
from flask_orphus import Request as orequest


@endpoint(name="mv_live_shorthand")
def default(resource) -> Response:
    _class: object = to_class(f"application.admin.{resource}Admin.{resource}Admin")
    model = to_class(f"application.models.{resource}.{resource}")
    method = orequest.input('method')
    args = orequest.input('args')
    data = orequest.all()
    del data['method']
    del data['args']
    record = model.find(args)
    # get success and error messages from model
    success_message = getattr(model(), "get_table_action_success_message", lambda : "Record updated successfully")()
    error_message = getattr(model(), "get_table_action_error_message", lambda : "Record update failed")()
    for action in _class().get_table_actions():
        if action['name'] == method:
            try:
                action['action'](record, data)
                flash(success_message, "success")
            except Exception as e:
                flash(error_message, "danger")
    redirect_response = redirect(request.referrer)
    redirect_response.headers['HX-Target'] = f"action-{ method }-resource-{ getattr(model(), 'edit_field') }"
    return redirect_response