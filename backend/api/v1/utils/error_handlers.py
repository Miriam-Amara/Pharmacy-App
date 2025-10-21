#!/usr/bin/env python3

"""
Defines custom error handlers for common HTTP exceptions.
"""


from flask import jsonify
from werkzeug.exceptions import HTTPException


def bad_request(error: HTTPException):
    """
    Handles 400 bad request errors
    """
    if error.description:
        return jsonify({"error": error.description}), 400
    return jsonify({"error": "Bad Request"}), 400


def unauthorized(error: HTTPException):
    """
    Handle 401 Unauthorized errors.
    """
    return jsonify({"error": "Unauthorized"}), 401


def forbidden(error: HTTPException):
    """
    Handle 403 Forbidden errors.
    """
    return jsonify({"error": "Forbidden"}), 403


def not_found(error: HTTPException):
    """
    Handle 404 Not Found errors.
    """
    if error.description:
        return jsonify({"error": error.description}), 404
    return jsonify({"Error": "Not Found"}), 404


def method_not_allowed(error: HTTPException):
    """
    Handle 405 Method Not Allowed errors.
    """
    if error.description:
        return jsonify({"error": error.description}), 405
    return jsonify({"Error": "Method Not allowed"}), 405


def conflict_error(error: HTTPException):
    """
    Handle 409 Conflict errors.
    """
    return jsonify({"error": error.description}), 409


def server_error(error: HTTPException):
    """
    Handle 500 Internal Server Error.
    """
    return jsonify({"error": "Internal Server Error"}), 500
