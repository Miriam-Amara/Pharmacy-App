#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String

from basemodel import Base, BaseModel


class Category(BaseModel, Base):
    """
    """
    __tablename__ = "categories"
    
    name = mapped_column(String(200))
    description = mapped_column(String(2000))
    employee_id = mapped_column(
        String(36),
        ForeignKey("employees.id"),
        ondelete="SET NULL",
    )
    added_by = relationship("Employee", backref="categories_added")
    products = relationship("Product", back_populates="category")
