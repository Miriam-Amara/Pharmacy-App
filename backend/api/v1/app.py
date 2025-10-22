#!/usr/bin/env python3

"""
Main Flask application setup for the Pharmacy API.
"""

from dotenv import load_dotenv
from flask import Flask, abort, request, g
from flask_bcrypt import Bcrypt
import logging
import os

from api.v1.auth.session_db_auth import SessionDBAuth
from api.v1.utils.error_handlers import (
    bad_request, unauthorized, forbidden, not_found, method_not_allowed,
    conflict_error, server_error
)
from api.v1.views import app_views
from models import storage


load_dotenv()
logger = logging.getLogger(__name__)
bcrypt = Bcrypt()
auth = SessionDBAuth()

def check_authentication():
    """
    Verifies session authentication for protected routes.
    """
    if not auth.require_auth(
        request.path,
        [
            "/api/v1/register/", "/api/v1/auth_session/login/"
        ]
    ):
        return
    if not auth.session_cookie():
        abort(401)
    
    employee = auth.current_employee()
    if not employee:
        abort(401)
    g.current_employee = employee

def close_db(exception: BaseException | None) -> None:
    """
    Closes the database session after each request.
    """
    storage.close()

def create_app(config_name: str | None=None) -> Flask:
    """
    Creates and configures the Flask application instance.
    """
    app = Flask(__name__)

    if config_name == "test":
        app.config.from_mapping(TESTING=True)
    else:
        app.config.from_mapping(TESTING=False)

    bcrypt.init_app(app) # type: ignore
    app.register_blueprint(app_views)
    app.before_request(check_authentication)
    app.teardown_appcontext(close_db)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(409, conflict_error)
    app.register_error_handler(500, server_error)

    return app


config_name = os.getenv("ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    host = os.getenv("PHARMACY_API_HOST", "0.0.0.0")
    port = int(os.getenv("PHARMACY_API_PORT", 5000))
    debug_mode = bool(os.getenv("DEBUG_MODE", False))
    app.run(host=host, port=port, threaded=True, debug=debug_mode)
    