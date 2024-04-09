import hashlib
import json
import secrets
from typing import Any

from flask import render_template_string

from mvlive.utils import to_class


class HasSnapshots:
    def from_snapshot(self, req_snapshot: dict[str, Any]):
        req_checksum: str = req_snapshot['snapshot']['checksum']
        print(req_snapshot)
        del req_snapshot['snapshot']['checksum']
        if 'children' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['children']
        if 'models' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['models']
        if 'actions' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['actions']
        if 'polls' in req_snapshot['snapshot']:
            del req_snapshot['snapshot']['polls']
        # pprint.pprint(req_snapshot['snapshot'])

        source_checksum: str = hashlib.md5(
            json.dumps(req_snapshot['snapshot'], sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()

        if source_checksum != req_checksum:
            raise Exception("Stop trying to hack me.")
        class_name: str = req_snapshot['snapshot']['class']
        data: dict[str, Any] = req_snapshot['snapshot']['data']
        #children = req_snapshot['snapshot']['children']


        _class: Any = to_class(f"templates.components.mvlive.{class_name}.{class_name}")()
        _class.__name__, _class.__class__.__name__ = class_name, class_name
        if getattr(_class, "key", None):
            print("checking if component key is set.......")
            key = getattr(_class, "key")
            print(f"found key {key}")
        else:
            key = f"mvlive_{_class.__name__.lower()}_{secrets.token_urlsafe(4)}"
        setattr(_class, "key", key)

        for prop in data.items():
            setattr(_class, prop[0], prop[1])
        return _class

    def to_snapshot(self, _class: Any):
        props: dict[str, Any] = self.get_props(_class)
        _class.key = props.get("key")
        print(_class, props)

        html: str = render_template_string(
            _class.render.__doc__,
            **props
        )

        # meta = self.dehydrate_properties(props)

        key = getattr(_class, "key", "")

        snapshot: dict[str, Any] = {
            "class": _class.__class__.__name__,
            "key": key,
            "data": props,
            # "html": html,
        }
        snapshot['checksum']: str = hashlib.md5(
            json.dumps(snapshot, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()

        return html, snapshot