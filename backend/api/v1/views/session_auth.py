#!/usr/bin/env python3

"""
Handles employee login and logout using session authentication.
"""


from dotenv import load_dotenv
from flask import abort, jsonify
import logging

from api.v1.views import app_views
from api.v1.auth.authentication import LoginAuth

load_dotenv()
logger = logging.getLogger(__name__)


@app_views.route(
        "/auth_session/login",
        strict_slashes=False,
        methods=["POST"]
    )
def login():
    """
    Logs in an employee and sets a session cookie.
    """
    login_auth = LoginAuth()
    cookie_name, session_id, employee_id = login_auth.login_employee()
    response_data = {
        "message": "Login successful",
        "employee_id": employee_id
    }
    response = jsonify(response_data)
    response.set_cookie(
        key=cookie_name,
        value=session_id,
        max_age=3600,
        secure=False,
        httponly=True
    )
    return response, 201


@app_views.route(
        "/auth_session/logout",
        strict_slashes=False,
        methods=["DELETE"]
    )
def logout():
    """
    Logs out an employee and clears their session.
    """
    from api.v1.app import auth

    if not auth.destroy_session():
        abort(404)
    return jsonify({}), 200
