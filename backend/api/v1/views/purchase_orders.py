#!/usr/bin/env python3

"""
Routes for managing purchase orders.
"""

from flask import abort, jsonify, g
from typing import Any

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    PurchaseOrderRegister,
    PurchaseOrderUpdate,
    validate_request_data,
)
from api.v1.utils.utility import DatabaseOp, get_obj
from models import storage
from models.purchase_order import PurchaseOrder
from models.purchase_order_item import PurchaseOrderItem


def get_purchase_order_items(order_item: PurchaseOrderItem) -> dict[str, Any]:
    """
    Return a purchase order item as a dictionary.
    """
    order_item_dict: dict[str, Any] = {}
    order_item_to_dict: dict[str, Any] = order_item.to_dict()
    for attr, value in order_item_to_dict.items():
        if attr == "purchase_order":
            continue
        if attr == "product":
            order_item_dict[attr] = value.name
        else:
            order_item_dict[attr] = value
    return order_item_dict


def get_purchase_order_dict(purchase_order: PurchaseOrder) -> dict[str, Any]:
    """
    Return a purchase order as a dictionary excluding related items.
    """
    purchase_order_dict = purchase_order.to_dict()
    for attr, value in purchase_order_dict.items():
        if attr == "brand":
            purchase_order_dict[attr] = value.name
        if attr == "added_by":
            purchase_order_dict[attr] = value.username
        if attr == "purchase_order_items":
            continue
    return purchase_order_dict


@app_views.route("/purchase_orders", strict_slashes=False, methods=["POST"])
@admin_only
def register_purchase_order():
    """
    Register a new purchase order.
    """
    admin = g.current_employee
    valid_data = validate_request_data(PurchaseOrderRegister)
    valid_data["employee_id"] = admin.id

    purchase_order = PurchaseOrder(**valid_data)
    db = DatabaseOp()
    db.save(purchase_order)

    purchase_order_dict = get_purchase_order_dict(purchase_order)
    return jsonify(purchase_order_dict), 201


@app_views.route(
    "/purchase_orders/<int:page_size>/<int:page_num>",
    strict_slashes=False,
    methods=["GET"],
)
@admin_only
def get_all_purchase_orders(page_size: int, page_num: int):
    """
    Get paginated list of all purchase orders.
    """
    purchase_orders_objects = storage.all(PurchaseOrder, page_size, page_num)
    if not purchase_orders_objects:
        abort(404, description="No purchase_order found")

    purchase_order_lists: list[dict[str, Any]] = []
    for purchase_order in purchase_orders_objects:
        purchase_order_dict = get_purchase_order_dict(purchase_order)
        purchase_order_lists.append(purchase_order_dict)
    return jsonify(purchase_order_lists), 200


@app_views.route(
    "purchase_orders/<purchase_order_id>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_purchase_order(purchase_order_id: str):
    """
    Get details of a purchase order by ID.
    """
    purchase_order = get_obj(PurchaseOrder, purchase_order_id)
    if not purchase_order:
        abort(404, description="Order does not exist")

    purchase_order_dict = get_purchase_order_dict(purchase_order)
    purchase_order_items: list[dict[str, Any]] = []
    for order_item in purchase_order.purchase_order_items:
        order_item = get_purchase_order_items(order_item)
        purchase_order_items.append(order_item)

    purchase_order_dict.update({"order_items": purchase_order_items})
    return jsonify(purchase_order_dict), 200


@app_views.route(
    "purchase_orders/<purchase_order_id>",
    strict_slashes=False,
    methods=["PUT"]
)
@admin_only
def update_purchase_order(purchase_order_id: str):
    """
    Update an existing purchase order.
    """
    valid_data = validate_request_data(PurchaseOrderUpdate)
    purchase_order = get_obj(PurchaseOrder, purchase_order_id)
    if not purchase_order:
        abort(404, description="Purchase_order does not exist")

    for attr, value in valid_data.items():
        setattr(purchase_order, attr, value)

    db = DatabaseOp()
    db.save(purchase_order)

    purchase_order_dict = get_purchase_order_dict(purchase_order)
    return jsonify(purchase_order_dict), 200


@app_views.route(
    "purchase_orders/<purchase_order_id>",
    strict_slashes=False,
    methods=["DELETE"]
)
@admin_only
def delete_purchase_order(purchase_order_id: str):
    """
    Delete a purchase order.
    """
    purchase_order = get_obj(PurchaseOrder, purchase_order_id)
    if not purchase_order:
        abort(404, description="Purchase_order does not exist")

    db = DatabaseOp()
    db.delete(purchase_order)
    db.commit()
    return jsonify({}), 200
