from flask import Flask, render_template, request, redirect, url_for, session
from flask_orphus.http import Session, Redirect, Request
from flask_orphus.routing.fs_router import endpoint
from flask_orphus import Request as orequest

from application.services.ADAuth import ADAuth


@endpoint(name="do_logout")
def do_logout():
    session.clear()
    return redirect('/auth/login')
