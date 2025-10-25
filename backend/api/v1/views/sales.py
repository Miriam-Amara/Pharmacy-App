#!/usr/bin/env python3

"""
Handles CRUD operations for sales via API routes.
"""

from flask import abort, jsonify, g
from typing import Any
import logging

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    SaleRegister,
    SaleUpdate,
    validate_request_data,
)
from api.v1.utils.utility import DatabaseOp, get_obj
from models import storage
from models.brand import Brand
from models.product import Product
from models.sale import Sale


logger = logging.getLogger(__name__)


def get_sale_dict(sale: Sale) -> dict[str, Any]:
    """
    Returns a serialized dictionary for a sale with readable fields.
    """
    sale_dict = sale.to_dict()
    sale_dict["product"] = getattr(sale.product, "name", None)
    sale_dict["brand"] = getattr(sale.brand, "name", None)
    sale_dict["added_by"] = getattr(sale.added_by, "username")
    return sale_dict


@app_views.route("/sales", strict_slashes=False, methods=["POST"])
@admin_only
def add_sale_item():
    """
    Creates a new sale record.
    """
    admin = g.current_employee

    valid_data = validate_request_data(SaleRegister)
    brand = get_obj(Brand, valid_data["brand_id"])
    product = get_obj(Product, valid_data["product_id"])

    if not brand:
        abort(404, description="Brand does not exist.")
    if not product:
        abort(404, description="Product does not exist.")

    valid_data["employee_id"] = admin.id
    sale = Sale(**valid_data)
    db = DatabaseOp()
    db.save(sale)

    sale_dict = get_sale_dict(sale)
    return jsonify(sale_dict), 201


@app_views.route(
    "/sales/<int:page_size>/<int:page_num>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_all_sales(page_size: int, page_num: int):
    """
    Retrieves all sales with pagination.
    """
    sales = storage.all(Sale, page_size, page_num)
    if not sales:
        abort(404, description="No sales found")

    sales_list: list[dict[str, Any]] = []
    for item in sales:
        item_dict = get_sale_dict(item)
        sales_list.append(item_dict)
    return jsonify(sales_list), 200


@app_views.route(
        "sales/<sale_id>",
        strict_slashes=False,
        methods=["GET"]
    )
@admin_only
def get_sale_item(sale_id: str):
    """
    Retrieves a single sale record by ID.
    """
    sale = get_obj(Sale, sale_id)
    if not sale:
        abort(404, description="Item does not exist")

    sale_dict = get_sale_dict(sale)
    return jsonify(sale_dict), 200


@app_views.route(
        "/sales/<sale_id>",
        strict_slashes=False,
        methods=["PUT"]
    )
@admin_only
def update_sale_item(sale_id: str):
    """
    Updates an existing sale record.
    """
    valid_data = validate_request_data(SaleUpdate)

    if "brand_id" in valid_data:
        brand = get_obj(Brand, valid_data["brand_id"])
        if not brand:
            abort(404, description="Brand does not exist.")
    if "product_id" in valid_data:
        product = get_obj(Product, valid_data["product_id"])
        if not product:
            abort(404, description="Product does not exist.")

    sale = get_obj(Sale, sale_id)
    if not sale:
        abort(404, description="Item does not exist")

    for attr, value in valid_data.items():
        setattr(sale, attr, value)

    db = DatabaseOp()
    db.save(sale)

    sale_dict = get_sale_dict(sale)
    return jsonify(sale_dict), 200


@app_views.route(
        "/sales/<sale_id>",
        strict_slashes=False,
        methods=["DELETE"]
    )
@admin_only
def delete_sale_item(sale_id: str):
    """
    Deletes a sale record by ID.
    """
    sale = get_obj(Sale, sale_id)
    if not sale:
        abort(404, description="Item does not exist")

    db = DatabaseOp()
    db.delete(sale)
    db.commit()
    return jsonify({}), 200
