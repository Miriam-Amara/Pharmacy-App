#!/usr/bin/env python3

"""
Defines Pydantic models, enums, and validation
utilities for request data.
"""

from enum import Enum
from flask import abort, request
from json import JSONDecodeError
from pydantic import (
    BaseModel,
    ValidationError,
    EmailStr,
    StringConstraints,
    StrictBool,
    PositiveFloat,
    PositiveInt,
    field_validator,
)
from typing import Any, Annotated, Type, TypeVar, Optional
import logging


T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class EmployeeRole(str, Enum):
    """
    Employee roles
    """

    salesperson = "salesperson"
    manager = "manager"


class PurchaseOrderStatus(Enum):
    """
    Purchase order statuses.
    """

    pending = "pending"
    in_progress = "in progress"
    complete = "complete"
    cancelled = "cancelled"


class ItemStatus(Enum):
    """
    Purchase order item statuses.
    """

    pending = "pending"
    supplied = "supplied"
    cancelled = "cancelled"


class PaymentStatus(Enum):
    """
    Payment statuses.
    """

    paid = "paid"
    unpaid = "unpaid"
    partial_payment = "partial payment"


class EmployeeLogin(BaseModel):
    """
    Schema for employee login validation.
    """

    email: Optional[EmailStr] = None
    username: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=100,
                strip_whitespace=True
            )
        ]
    ] = None
    password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]

    @field_validator("email", "username")
    @classmethod
    def lowercase_email_username(cls, v: str) -> str:
        """
        Convert email/username to lowercase.
        """
        return v.lower()

    @field_validator("password")
    @classmethod
    def check_complexity(cls, v: str):
        """
        Ensure password contains uppercase and digit.
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Must contain an uppercase")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain a digit")
        return v


class EmployeeRegister(BaseModel):
    """
    Schema for employee registration validation.
    """

    first_name: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=200,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    middle_name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    last_name: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=200,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    username: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=200,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    email: EmailStr
    password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=200,
            strip_whitespace=True
        )
    ]
    home_address: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=500,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    role: EmployeeRole
    is_admin: Optional[StrictBool] = None

    @field_validator("email", "role", mode="before")
    @classmethod
    def lowercase_email_username(cls, v: str) -> str:
        """
        Convert email and role to lowercase.
        """
        return v.lower()

    @field_validator("password")
    @classmethod
    def check_complexity(cls, v: str):
        """
        Ensure password contains uppercase and digit.
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Must contain an uppercase")
        if not any(c.isdigit() for c in v):
            raise ValueError("Must contain a digit")
        return v


class EmployeeUpdate(BaseModel):
    """
    Schema for updating employee details.
    """

    first_name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    middle_name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    last_name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    home_address: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=10,
                max_length=500,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    role: Optional[EmployeeRole] = None
    is_admin: Optional[StrictBool] = None


class BrandRegister(BaseModel):
    """
    Schema for brand creation.
    """

    name: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=200,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    is_active: Optional[StrictBool] = True


class BrandUpdate(BaseModel):
    """
    Schema for updating brand details.
    """

    name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    is_active: Optional[StrictBool] = True


class CategoryRegister(BaseModel):
    """
    Schema for category creation.
    """

    name: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=200,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    description: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=2000,
            to_lower=True,
            strip_whitespace=True
        ),
    ]


class CategoryUpdate(BaseModel):
    """
    Schema for updating category details.
    """

    name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    description: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=2000,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None


class ProductRegister(BaseModel):
    """
    Schema for product creation.
    """

    name: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=200,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    selling_price: Annotated[float, PositiveFloat]
    category_id: Annotated[
        str,
        StringConstraints(
            min_length=36,
            max_length=36,
            to_lower=True,
            strip_whitespace=True
        ),
    ]


class ProductUpdate(BaseModel):
    """
    Schema for updating product details.
    """

    name: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=3,
                max_length=200,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    selling_price: Optional[Annotated[float, PositiveFloat]] = None
    category_id: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=36,
                max_length=36,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None


class PurchaseOrderRegister(BaseModel):
    """
    Schema for purchase order creation.
    """

    status: Optional[PurchaseOrderStatus] = PurchaseOrderStatus.pending
    brand_id: Annotated[
        str,
        StringConstraints(
            min_length=36,
            max_length=36,
            to_lower=True,
            strip_whitespace=True
        ),
    ]


class PurchaseOrderUpdate(BaseModel):
    """
    Schema for updating purchase order.
    """

    status: Optional[PurchaseOrderStatus] = PurchaseOrderStatus.pending
    brand_id: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=36,
                max_length=36,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None


class PurchaseOrderItemRegister(BaseModel):
    """
    Schema for adding items to a purchase order.
    """

    product_id: Annotated[
        str,
        StringConstraints(
            min_length=36,
            max_length=36,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    quantity: Annotated[int, PositiveInt]
    unit_cost_price: Annotated[float, PositiveFloat]
    total_cost_price: Annotated[float, PositiveFloat]
    payment_status: PaymentStatus
    item_status: Optional[ItemStatus] = ItemStatus.pending


class PurchaseOrderItemUpdate(BaseModel):
    """
    Schema for updating purchase order items.
    """

    product_id: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=36,
                max_length=36,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    quantity: Optional[Annotated[int, PositiveInt]] = None
    unit_cost_price: Optional[Annotated[float, PositiveFloat]] = None
    total_cost_price: Optional[Annotated[float, PositiveFloat]] = None
    payment_status: Optional[PaymentStatus] = None
    item_status: Optional[ItemStatus] = None


class SaleRegister(BaseModel):
    """
    Schema for sales creation.
    """

    product_id: Annotated[
        str,
        StringConstraints(
            min_length=36,
            max_length=36,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    brand_id: Annotated[
        str,
        StringConstraints(
            min_length=36,
            max_length=36,
            to_lower=True,
            strip_whitespace=True
        ),
    ]
    quantity: Annotated[int, PositiveInt]
    unit_selling_price: Annotated[float, PositiveFloat]
    total_selling_price: Annotated[float, PositiveFloat]


class SaleUpdate(BaseModel):
    """
    Schema for updating sales records.
    """

    product_id: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=36,
                max_length=36,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    brand_id: Optional[
        Annotated[
            str,
            StringConstraints(
                min_length=36,
                max_length=36,
                to_lower=True,
                strip_whitespace=True
            ),
        ]
    ] = None
    quantity: Optional[Annotated[int, PositiveInt]] = None
    unit_selling_price: Optional[Annotated[float, PositiveFloat]] = None
    total_selling_price: Optional[Annotated[float, PositiveFloat]] = None


def get_request_data() -> dict[str, Any]:
    """
    Extract and validate JSON from the request.
    """
    try:
        request_data: dict[str, Any] = request.get_json()
    except JSONDecodeError:
        abort(400, description="Not a json")

    return request_data


def validate_request_data(validation_cls: Type[T]) -> dict[str, Any]:
    """
    Validate incoming request data against a Pydantic model.
    """
    request_data = get_request_data()

    if not issubclass(validation_cls, BaseModel):  # type: ignore
        abort(500, description="Validation class must inherit from BaseModel")

    try:
        valid_data = validation_cls(**request_data)
    except ValidationError as e:
        abort(400, description=e.errors())

    if not valid_data.model_dump(exclude=None):
        abort(400, description="Request data cannot be empty")
    return valid_data.model_dump(exclude_unset=True)
