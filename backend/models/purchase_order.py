#!/usr/bin/env python3

"""
Purchase order model.
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Enum
import enum

from models.basemodel import Base, BaseModel


class OrderStatus(enum.Enum):
    """Represents the current stage of a purchase order."""

    pending = "pending"
    in_progress = "in progress"
    complete = "complete"
    cancelled = "cancelled"


class PurchaseOrder(BaseModel, Base):
    """Represents a purchase order record."""

    __tablename__ = "purchase_orders"

    status = mapped_column(
        Enum(OrderStatus, name="orderstatus", create_type=False),
        default="pending"
    )
    brand_id = mapped_column(
        String(36),
        ForeignKey("brands.id", ondelete="SET NULL"),
    )
    employee_id = mapped_column(
        String(36),
        ForeignKey("employees.id", ondelete="SET NULL")
    )

    purchase_order_items = relationship(
        "PurchaseOrderItem", back_populates="purchase_order"
    )
    brand = relationship("Brand", back_populates="purchase_orders")
    added_by = relationship("Employee", backref="purchase_orders_added")
