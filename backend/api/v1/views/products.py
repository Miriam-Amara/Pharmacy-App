#!/usr/bin/env python3

"""
Routes for managing products.
"""

from flask import abort, jsonify, g
from typing import Any
import logging

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    ProductRegister,
    ProductUpdate,
    validate_request_data,
)
from api.v1.utils.utility import DatabaseOp, get_obj
from models import storage
from models.product import Product
from models.category import Category


logger = logging.getLogger(__name__)


def get_product_dict(product: Product) -> dict[str, Any]:
    """
    Return product data excluding relations.
    """
    product_dict = product.to_dict()
    product_dict["category"] = getattr(product.category, "name", None)
    product_dict["added_by"] = getattr(
        product.added_by, "username", None
    )
    return product_dict


@app_views.route(
        "/products",
        strict_slashes=False,
        methods=["POST"]
    )
@admin_only
def register_product():
    """
    Create a new product.
    """
    admin = g.current_employee
    valid_data = validate_request_data(ProductRegister)
    valid_data["employee_id"] = admin.id

    if "category_id" in valid_data:
        category = get_obj(Category, valid_data["category_id"])
        if not category:
            abort(404, description="Category does not exist.")
        valid_data["category"] = category

    product = Product(**valid_data)
    product.added_by = admin
    db = DatabaseOp()
    db.save(product)

    product_dict = get_product_dict(product)
    return jsonify(product_dict), 201


@app_views.route(
    "/products/<int:page_size>/<int:page_num>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_all_products(page_size: int, page_num: int):
    """
    Get paginated list of products.
    """
    products_objects = storage.all(Product, page_size, page_num)
    if not products_objects:
        abort(404, description="No product found")

    product_lists: list[dict[str, Any]] = []
    for product in products_objects:
        product_dict = get_product_dict(product)
        product_lists.append(product_dict)
    return jsonify(product_lists), 200


@app_views.route(
        "products/<product_id>",
        strict_slashes=False,
        methods=["GET"]
    )
@admin_only
def get_product(product_id: str):
    """
    Get a single product by ID.
    """
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    product_dict = get_product_dict(product)
    return jsonify(product_dict), 200


@app_views.route(
        "products/<product_id>",
        strict_slashes=False,
        methods=["PUT"]
    )
@admin_only
def update_product(product_id: str):
    """
    Update product details.
    """
    valid_data = validate_request_data(ProductUpdate)
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    if "category_id" in valid_data:
        category = get_obj(Category, valid_data["category_id"])
        if not category:
            abort(404, description="Category does not exist.")
        valid_data["category"] = category

    for attr, value in valid_data.items():
        setattr(product, attr, value)

    db = DatabaseOp()
    db.save(product)

    product_dict = get_product_dict(product)
    return jsonify(product_dict), 200


@app_views.route(
        "products/<product_id>",
        strict_slashes=False,
        methods=["DELETE"]
    )
@admin_only
def delete_product(product_id: str):
    """
    Delete a product.
    """
    product = get_obj(Product, product_id)
    if not product:
        abort(404, description="Product does not exist")

    db = DatabaseOp()
    db.delete(product)
    db.commit()
    return jsonify({}), 200
