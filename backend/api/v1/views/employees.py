#!/usr/bin/env python3

"""
Defines routes for employee registration and management.
"""

from flask import abort, jsonify
import logging

from api.v1.auth.authorization import admin_only
from api.v1.views import app_views
from api.v1.utils.request_data_validation import (
    EmployeeRegister,
    EmployeeUpdate,
    validate_request_data,
)
from api.v1.utils.utility import (
    DatabaseOp, get_obj, check_email_username_exists
)
from models import storage
from models.employee import Employee


logger = logging.getLogger(__name__)

@app_views.route("/register", strict_slashes=False, methods=["POST"])
def register_employee():
    """
    Registers a new employee.
    """
    from api.v1.app import bcrypt
    valid_data = validate_request_data(EmployeeRegister)
    
    check_email_username_exists(valid_data)

    valid_data["password"] = bcrypt.generate_password_hash(  # type: ignore
        valid_data["password"]
    ).decode("utf-8")
    employee = Employee(**valid_data)

    db = DatabaseOp()
    db.save(employee)

    employee_dict = employee.to_dict()
    return jsonify(employee_dict), 201


@app_views.route(
    "/employees/<int:page_size>/<int:page_num>",
    strict_slashes=False,
    methods=["GET"]
)
@admin_only
def get_all_employees(page_size: int, page_num: int):
    """
    Retrieves all employees with pagination.
    """
    employees_objects = storage.all(Employee, page_size, page_num)
    if not employees_objects:
        abort(404, description="No employee found")

    all_employees = [
        employee.to_dict() for employee in employees_objects
    ]
    return jsonify(all_employees), 200


@app_views.route(
        "/employees/<employee_id>",
        strict_slashes=False,
        methods=["GET"]
    )
def get_employee(employee_id: str):
    """
    Retrieves a single employee by ID.
    """
    employee = get_obj(Employee, employee_id)
    if not employee:
        abort(404, description="User does not exist")
    employee_dict = employee.to_dict()
    return jsonify(employee_dict), 200


@app_views.route(
        "/employees/<employee_id>",
        strict_slashes=False,
        methods=["PUT"]
    )
def update_employee(employee_id: str):
    """
    Updates an employee’s details.
    """
    valid_data = validate_request_data(EmployeeUpdate)

    employee = get_obj(Employee, employee_id)
    if not employee:
        abort(404, description="User does not exist")

    for attr, value in valid_data.items():
        setattr(employee, attr, value)

    db = DatabaseOp()
    db.save(employee)

    employee_dict = employee.to_dict()
    return jsonify(employee_dict), 200


@app_views.route(
        "/employees/<employee_id>",
        strict_slashes=False,
        methods=["DELETE"]
    )
@admin_only
def delete_employee(employee_id: str):
    """
    Deletes an employee by ID.
    """
    employee = get_obj(Employee, employee_id)
    if not employee:
        abort(404, description="User does not exist")

    db = DatabaseOp()
    db.delete(employee)
    db.commit()
    return jsonify({}), 200
