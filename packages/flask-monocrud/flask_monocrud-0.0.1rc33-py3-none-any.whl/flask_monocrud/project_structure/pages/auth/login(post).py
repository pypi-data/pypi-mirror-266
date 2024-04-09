from flask import request
from flask_orphus.http import Session, Redirect, Request
from flask_orphus.routing.fs_router import endpoint
from flask_orphus import Request as orequest

from application.services.ADAuth import ADAuth

from flask_monocrud.helpers import from_config


@endpoint(name="do_login")
def do_login():
    username = orequest.input('username')
    password = orequest.input('password')
    authenticated_user = ADAuth.raven_driver(username, password)
    if authenticated_user:
        return Redirect.to(from_config("LOGIN_REDIRECT_URL")).route()
    return Redirect.to("/auth/login").route()
