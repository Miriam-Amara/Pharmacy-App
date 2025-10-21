#!/usr/bin/env python3

"""
Purchase order item model and enums.
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, Float, Enum
import enum

from models.basemodel import Base, BaseModel


class ItemStatus(enum.Enum):
    """Status of a purchased item."""

    pending = "pending"
    supplied = "supplied"
    cancelled = "cancelled"


class PaymentStatus(enum.Enum):
    """Payment state for an order item."""

    paid = "paid"
    unpaid = "unpaid"
    partial_payment = "partial payment"


class PurchaseOrderItem(BaseModel, Base):
    """Represents an individual item in a purchase order."""

    __tablename__ = "purchase_order_items"

    purchase_order_id = mapped_column(
        String(36),
        ForeignKey("purchase_orders.id", ondelete="SET NULL"),
    )
    product_id = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="SET NULL"),
    )
    quantity = mapped_column(Integer, default=0)
    unit_cost_price = mapped_column(Float, default=0)
    total_cost_price = mapped_column(Float, default=0)
    payment_status = mapped_column(Enum(PaymentStatus), nullable=False)
    item_status = mapped_column(Enum(ItemStatus), default="pending")
    purchase_order = relationship(
        "PurchaseOrder", back_populates="purchase_order_items"
    )
    product = relationship("Product", back_populates="purchases")
