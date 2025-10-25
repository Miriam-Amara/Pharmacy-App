#!/usr/bin/env python3

"""
Routes for managing purchase order items.
"""

from flask import abort, jsonify
from typing import Any
import logging

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    PurchaseOrderItemRegister,
    PurchaseOrderItemUpdate,
    validate_request_data,
)
from api.v1.utils.utility import DatabaseOp, get_obj
from models import storage
from models.product import Product
from models.purchase_order import PurchaseOrder
from models.purchase_order_item import PurchaseOrderItem


logger = logging.getLogger(__name__)


def get_order_item_dict(order_item: PurchaseOrderItem) -> dict[str, Any]:
    """
    Return purchase order item data excluding relations.
    """
    order_item_dict = order_item.to_dict()
    order_item_dict["product"] = getattr(order_item.product, "name", None)
    return order_item_dict


@app_views.route(
    "/purchase_orders/<purchase_order_id>/purchase_order_items",
    strict_slashes=False,
    methods=["POST"],
)
@admin_only
def add_purchase_item(purchase_order_id: str):
    """
    Add a new purchase order item.
    """
    valid_data = validate_request_data(PurchaseOrderItemRegister)
    
    product = get_obj(Product, valid_data["product_id"])
    if not product:
        abort(404, description="Product does not exist.")

    purchase_order = get_obj(PurchaseOrder, purchase_order_id)
    if not purchase_order:
        abort(404, description="Order does not exist")

    valid_data["purchase_order_id"] = purchase_order.id
    purchase_order_item = PurchaseOrderItem(**valid_data)

    db = DatabaseOp()
    db.save(purchase_order_item)

    order_item_dict = get_order_item_dict(purchase_order_item)
    return jsonify(order_item_dict), 201


@app_views.route(
    "/purchases/<int:page_size>/<int:page_num>", strict_slashes=False, methods=["GET"]
)
@admin_only
def get_all_purchases(page_size: int, page_num: int):
    """
    Get paginated list of all purchase order items.
    """
    purchases = storage.all(PurchaseOrderItem, page_size, page_num)
    if not purchases:
        abort(404, description="No purchases found")

    purchases_list: list[dict[str, Any]] = []
    for item in purchases:
        item_dict = get_order_item_dict(item)
        purchases_list.append(item_dict)
    return jsonify(purchases_list), 200


@app_views.route(
    "/purchase_orders/<order_id>/purchase_order_items/<order_item_id>",
    strict_slashes=False,
    methods=["GET"],
)
@admin_only
def get_purchase_item(order_id: str, order_item_id: str):
    """
    Get a single purchase order item by ID.
    """
    purchase_order = get_obj(PurchaseOrder, order_id)
    if not purchase_order:
        abort(404, description="Order does not exist.")

    purchase_item = get_obj(PurchaseOrderItem, order_item_id)
    if not purchase_item:
        abort(404, description="Item does not exist.")

    item_dict = get_order_item_dict(purchase_item)
    return jsonify(item_dict), 200


@app_views.route(
    "/purchase_orders/<order_id>/purchase_order_items/<order_item_id>",
    strict_slashes=False,
    methods=["PUT"],
)
@admin_only
def update_purchase_order_item(order_id: str, order_item_id: str):
    """
    Update details of a purchase order item.
    """
    valid_data = validate_request_data(PurchaseOrderItemUpdate)

    if "product_id" in valid_data:
        product = get_obj(Product, valid_data["product_id"])
        if not product:
            abort(404, description="Product does not exist.")

    purchase_order = get_obj(PurchaseOrder, order_id)
    if not purchase_order:
        abort(404, description="Order does not exist.")

    order_item = get_obj(PurchaseOrderItem, order_item_id)
    if not order_item:
        abort(404, description="Item does not exist.")

    for attr, value in valid_data.items():
        setattr(order_item, attr, value)

    db = DatabaseOp()
    db.save(order_item)

    order_item_dict = get_order_item_dict(order_item)
    return jsonify(order_item_dict), 200


@app_views.route(
    "/purchase_orders/<order_id>/purchase_order_items/<order_item_id>",
    strict_slashes=False,
    methods=["DELETE"],
)
@admin_only
def delete_purchase_order_item(order_id: str, order_item_id: str):
    """
    Delete a purchase order item.
    """
    purchase_order = get_obj(PurchaseOrder, order_id)
    if not purchase_order:
        abort(404, description="Order does not exist.")

    order_item = get_obj(PurchaseOrderItem, order_item_id)
    if not order_item:
        abort(404, description="Item does not exist.")

    db = DatabaseOp()
    db.delete(order_item)
    db.commit()
    return jsonify({}), 200
