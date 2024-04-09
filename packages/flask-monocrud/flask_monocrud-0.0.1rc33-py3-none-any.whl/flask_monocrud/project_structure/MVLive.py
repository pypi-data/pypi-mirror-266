import functools
import hashlib
import json
import pprint
import secrets
from dataclasses import dataclass, field
from pydoc import locate
from typing import Any, List, AnyStr

from flask import render_template_string
from masoniteorm.collection import Collection

from mvlive.traits.has_actions import HasActions
from mvlive.traits.has_props import HasProps
from mvlive.traits.has_renders import HasRenders
from mvlive.traits.has_snapshots import HasSnapshots


def component(cls) -> 'cls':
    @functools.wraps(cls, updated=())
    class DecoratedClass(cls):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__class__.__name__ = cls.__name__
            cls.key = f"mvlive_{cls.__name__.lower()}_{secrets.token_urlsafe(4)}"
            cls.mvlive__locked = []
            cls.mvlive__session = []
            # if hasattr(cls, 'mount'):
            #     cls.__init__ = cls.mount

    DecoratedClass.__name__ = cls.__name__
    return DecoratedClass


@dataclass
class HandleEvents:
    listeners: list[dict[str, Any]] = field(default_factory=list)

    def get_listeners(self):
        return self.listeners

    def dispatch(self, event, **params):
        event = Event(event, params)
        return event


@dataclass
class Event:
    name_: str = field(default_factory=str)
    params: dict = field(default_factory=dict)
    this: bool = field(default_factory=bool)
    component: object = field(default_factory=object)

    def this_(self):
        self.this = True
        return self.this

    def component_(self, name):
        self.component = name
        return self

    def to(self, name):
        return self.component_(name)

    def serialize(self):
        output = {
            "name": self.name_,
            "params": self.params
        }
        if self.this:
            output.update({"this": True})
        if self.component:
            output.update({"to": self.component})


class MVLive(HasRenders, HasProps, HasSnapshots, HasActions):
    pass
