#!/usr/bin/env python3

"""

"""

from dotenv import load_dotenv
from flask import Flask, abort
import os

from api.v1.utils.error_handlers import (
    bad_request, unauthorized, forbidden, not_found, method_not_allowed,
    conflict_error, server_error
)
from api.v1.views import app_views
from models import storage


def close_db(exception: BaseException | None) -> None:
    """
    """
    storage.close()

def create_app(config_name: str | None=None) -> Flask:
    """
    """
    app = Flask(__name__)

    if config_name == "test":
        app.config.from_mapping(TESTING=True)
    else:
        app.config.from_mapping(TESTING=False)

    app.register_blueprint(app_views)
    app.teardown_appcontext(close_db)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(409, conflict_error)
    app.register_error_handler(500, server_error)

    return app


if __name__ == "__main__":
    load_dotenv()

    env = os.getenv("ENV")
    debug_mode = bool(os.getenv("DEBUG_MODE", False))
    if not env:
        abort(500)
    
    host = os.getenv("UNIBENENGVAULT_API_HOST", "0.0.0.0")
    port = int(os.getenv("UNIBENENGVAULT_API_PORT", 5000))
    app = create_app(env)
    app.run(host=host, port=port, threaded=True, debug=debug_mode)
    