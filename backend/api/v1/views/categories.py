#!/usr/bin/env python3

"""
Defines routes for category management operations.
"""

from flask import abort, jsonify, g
from typing import Any
import logging

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    CategoryRegister,
    CategoryUpdate,
    validate_request_data,
)
from api.v1.utils.utility import DatabaseOp, get_obj
from models import storage
from models.category import Category


logger = logging.getLogger(__name__)

def get_category_dict(category: Category) -> dict[str, Any]:
    """
    Converts a Category object to a dictionary
    excluding related fields.
    """
    
    category_dict = category.to_dict()
    category_dict["added_by"] = getattr(category.added_by, "username", None)

    return category_dict


@app_views.route(
        "/categories",
        strict_slashes=False,
        methods=["POST"]
    )
@admin_only
def register_category():
    """
    Creates a new category.
    """
    admin = g.current_employee
    valid_data = validate_request_data(CategoryRegister)
    valid_data["employee_id"] = admin.id

    category = Category(**valid_data)
    category.added_by = admin
    db = DatabaseOp()
    db.save(category)

    category_dict = get_category_dict(category)
    return jsonify(category_dict), 201


@app_views.route(
    "/categories/<int:page_size>/<int:page_num>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_all_categories(page_size: int, page_num: int):
    """
    Retrieves all categories with pagination.
    """
    categories_objects = storage.all(Category, page_size, page_num)
    if not categories_objects:
        abort(404, description="No category found")

    category_lists: list[dict[str, Any]] = []
    for category in categories_objects:
        category_dict = get_category_dict(category)
        category_lists.append(category_dict)
    return jsonify(category_lists), 200


@app_views.route(
        "categories/<category_id>",
        strict_slashes=False,
        methods=["GET"]
    )
@admin_only
def get_category(category_id: str):
    """
    Retrieves a single category by ID.
    """
    category = get_obj(Category, category_id)
    if not category:
        abort(404, description="Category does not exist")

    category_dict = get_category_dict(category)
    return jsonify(category_dict), 200


@app_views.route(
        "categories/<category_id>",
        strict_slashes=False,
        methods=["PUT"]
    )
@admin_only
def update_category(category_id: str):
    """
    Updates a category’s details.
    """
    valid_data = validate_request_data(CategoryUpdate)
    category = get_obj(Category, category_id)
    if not category:
        abort(404, description="Category does not exist")

    for attr, value in valid_data.items():
        setattr(category, attr, value)

    db = DatabaseOp()
    db.save(category)

    category_dict = get_category_dict(category)
    return jsonify(category_dict), 200


@app_views.route(
        "categories/<category_id>",
        strict_slashes=False,
        methods=["DELETE"]
    )
@admin_only
def delete_category(category_id: str):
    """
    Deletes a category by ID.
    """
    category = get_obj(Category, category_id)
    if not category:
        abort(404, description="Category does not exist")

    db = DatabaseOp()
    db.delete(category)
    db.commit()
    return jsonify({}), 200
