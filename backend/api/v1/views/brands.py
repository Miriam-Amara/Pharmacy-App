#!/usr/bin/env python3

"""
Defines routes for brand management operations.
"""

from flask import abort, jsonify, g
from typing import Any
import logging

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    BrandRegister,
    BrandUpdate,
    validate_request_data,
)
from api.v1.utils.utility import DatabaseOp, get_obj
from models import storage
from models.brand import Brand


logger = logging.getLogger(__name__)

def get_brand_dict(brand: Brand) -> dict[str, Any]:
    """
    Converts a Brand object to a dictionary excluding related fields.
    """
    brand_dict = brand.to_dict()
    brand_dict["added_by"] = getattr(brand.added_by, "username", None)
    return brand_dict


@app_views.route("/brands", strict_slashes=False, methods=["POST"])
@admin_only
def register_brand():
    """
    Creates a new brand.
    """
    admin = g.current_employee
    valid_data = validate_request_data(BrandRegister)
    valid_data["employee_id"] = admin.id

    brand = Brand(**valid_data)
    brand.added_by = admin
    db = DatabaseOp()
    db.save(brand)

    brand_dict = get_brand_dict(brand)
    return jsonify(brand_dict), 201


@app_views.route(
    "/brands/<int:page_size>/<int:page_num>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_all_brands(page_size: int, page_num: int):
    """
    Retrieves all brands with pagination.
    """
    brands_objects = storage.all(Brand, page_size, page_num)
    if not brands_objects:
        abort(404, description="No brand found")

    brand_lists: list[dict[str, Any]] = []
    for brand in brands_objects:
        brand_dict = get_brand_dict(brand)
        brand_lists.append(brand_dict)
    return jsonify(brand_lists), 200


@app_views.route(
        "brands/<brand_id>",
        strict_slashes=False,
        methods=["GET"]
    )
@admin_only
def get_brand(brand_id: str):
    """
    Retrieves a single brand by ID.
    """
    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    brand_dict = get_brand_dict(brand)
    return jsonify(brand_dict), 200


@app_views.route(
        "brands/<brand_id>",
        strict_slashes=False,
        methods=["PUT"]
    )
@admin_only
def update_brand(brand_id: str):
    """
    Updates brand details.
    """
    valid_data = validate_request_data(BrandUpdate)
    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    for attr, value in valid_data.items():
        setattr(brand, attr, value)

    db = DatabaseOp()
    db.save(brand)

    brand_dict = get_brand_dict(brand)
    return jsonify(brand_dict), 200


@app_views.route(
        "brands/<brand_id>",
        strict_slashes=False,
        methods=["DELETE"]
    )
@admin_only
def delete_brand(brand_id: str):
    """
    Deletes a brand by ID.
    """
    brand = get_obj(Brand, brand_id)
    if not brand:
        abort(404, description="Brand does not exist")

    db = DatabaseOp()
    db.delete(brand)
    db.commit()
    return jsonify({}), 200
