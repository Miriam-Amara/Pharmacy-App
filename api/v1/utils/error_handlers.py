#!/usr/bin/env python3

"""
"""


from flask import jsonify
from werkzeug.exceptions import HTTPException

def bad_request(error: HTTPException):
    """Handles 400 bad request errors"""
    if error.description:
        return jsonify({"error": error.description}), 400
    return jsonify({"error": "Bad Request"}), 400

def unauthorized(error: HTTPException):
    """
    """ 
    return jsonify({"error": "Unauthorized"}), 401

def forbidden(error: HTTPException):
    """
    """
    return jsonify({"error": "Forbidden"}), 403

def not_found(error: HTTPException):
    """Handles 404 request errors"""
    if error.description:
        return jsonify({"error": error.description}), 404
    return jsonify({"Error": "Not Found"}), 404

def method_not_allowed(error: HTTPException):
    """Handles 405 request errors"""
    if error.description:
        return jsonify({"error": error.description}), 405
    return jsonify({"Error": "Method Not allowed"}), 405

def conflict_error(error: HTTPException):
    """Handles data conflict errors"""
    return jsonify({"error": error.description}), 409

def server_error(error: HTTPException):
    """Handles 500 server request errors"""
    return jsonify({"error": "Internal Server Error"}), 500
