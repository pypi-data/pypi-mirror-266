import socket

import masoniteorm
import pywintypes
import win32security
from flask import session, request, redirect, url_for, abort

from flask_monocrud import to_class
from flask_monocrud.helpers import from_config


class ADAuth:
    @staticmethod
    def raven_driver(username, password):
        try:
            auth_model = to_class(from_config("AUTH_MODEL"))
        except AttributeError:
            to_class("application.models.User.User")
        username = username.lower()
        domain = from_config("AD_DOMAIN")
        print(domain)
        # Get user IP Address
        try:
            ip = str(socket.gethostbyaddr(request.remote_addr)[0])
        except socket.herror:
            ip = 'Unresolved'
        try:
            token = win32security.LogonUser(
                username,
                domain,
                password,
                win32security.LOGON32_LOGON_NETWORK,
                win32security.LOGON32_PROVIDER_DEFAULT)
            authenticated = bool(token)
            if authenticated:
                session['username'] = username
                session['password'] = password
                try:
                    authenticated_user = auth_model.where(from_config("AUTH_USERNAME_FIELD"), username).first()
                    return authenticated_user
                except masoniteorm.exceptions.QueryException:
                    abort(403)
        except pywintypes.error:
            return None
