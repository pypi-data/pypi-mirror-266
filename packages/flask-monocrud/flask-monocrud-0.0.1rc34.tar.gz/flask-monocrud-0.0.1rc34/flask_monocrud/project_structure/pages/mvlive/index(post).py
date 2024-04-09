import json
import pprint
from typing import Dict, Any, Optional

from MVLive import MVLive
from flask import request, Response
from flask_orphus.routing.fs_router import endpoint


@endpoint(name="mv_live")
def default() -> dict[str, Any]:
    req = request.json
    _class: object = MVLive().from_snapshot(req)

    if req.get('method'):
        method = req.get('method')
        args = req.get('args')
        if method != "emit":
            component = MVLive().call_method(_class, method, *tuple(args.split(",")))
        else:
            component = MVLive().call_event_handler(_class, method, args)

    if req.get('update_property'):
        req_updated_prop = req.get('update_property')
        MVLive().set_props(_class, req_updated_prop[0], req_updated_prop[1])
        component = _class
    html, snapshot = MVLive().to_snapshot(component)
    #print(html)
    return {
        "html": html, "snapshot": snapshot
    }
