from typing import Any, NoReturn
from flask_orphus.http import Session
from masoniteorm.collection import Collection


class HasProps:
    def get_props(self, component):
        props: dict[str, Any] = dict()
        method_list = [attribute for attribute in dir(component) if
                       callable(getattr(component, attribute)) and attribute.startswith('__') is False]

        for key in component.__dict__.items():
            if key[0].startswith("_"):
                continue
            if key[0] in method_list:
                continue
            else:
                props[f'{key[0]}'] = key[1]
        return props

    def set_props(self, _class, prop, val) -> NoReturn:
        if prop in _class.mvlive__locked:
            raise AttributeError(f"Property [{prop}] is locked from client-side editing.")
        # generate names for hook methods using prop name
        updated_hook: str = f'updated_{prop}'
        updating_hook: str = f'updating_{prop}'

        if hasattr(_class, 'updating'):
            _class.updating(prop, val)

        if hasattr(_class, updating_hook):
            getattr(_class, updating_hook)(val)

        if "." in prop:
            self.access_nested_dict_in_component(_class, prop, val)
        else:
            setattr(_class, prop, val)


        new_val = getattr(_class, prop)
        if hasattr(_class, 'updated'):
            _class.updated(prop, new_val)

        if hasattr(_class, updated_hook):
            getattr(_class, updated_hook)(new_val)

        Session().set(prop, new_val)



    def dehydrate_props(self, props):
        data = {}
        meta = {}

        for key in props.items():
            if isinstance(key[1], Collection):
                value = key[1].to_dict()
                meta[key[0]] = 'collection'
                data[key[1]] = value
            else:
                pass
        return data, meta

    def access_nested_dict_in_component(self, _class: Any, prop: str, val: str):
        props: dict[str, Any] = self.get_props(_class)
        for key in props.keys():
            if key == prop.split('.')[0]:
                _class.__dict__[key][prop.split('.')[1]] = val
