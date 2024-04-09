import json
from typing import Any, NoReturn

from flask_orphus.http import Session

from mvlive.traits.Bootable import Bootable
from mvlive.utils import dict_diff_changed_values


class HasActions:
    def call_method(self, component: Any, method: str, *args) -> NoReturn:
        props = self.get_props(component)
        Bootable.init_bootable_hook(_class=component)

        if "__NOVAL__" in args:
            args: tuple | list = ()
        else:
            args = [json.loads(x) for x in args]

        # Perform action then get new props
        getattr(component, method)(*args)
        new_props = self.get_props(component)
        for item in dict_diff_changed_values(props, new_props):
            self.set_props(component, item, new_props.get(item))
            Session().set(item, new_props.get(item))
        print(new_props, ":::::::::::::::::::::")
        return component


    def call_event_handler(self, component: Any, parsed_method: str, param: Any):
        props: dict[str, Any] = self.get_props(component)
        Bootable.init_bootable_hook(_class=component)


        # print(_class, parsed_method, json.loads(param))
        args_list: list[str] = [json.loads(x) for x in param.split(",")]
        if 'listeners' in props:
            event: str = args_list[0]
            args_list.pop(0)
            print(args_list)
            if args_list[0] != "__NOVAL__":
                getattr(component, props['listeners'][event])(*tuple(args_list))
            else:
                getattr(component, props['listeners'][event])()

        return component