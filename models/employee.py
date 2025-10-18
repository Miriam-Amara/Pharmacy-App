#!/usr/bin/env python3

"""
"""

from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Boolean

from basemodel import Base, BaseModel


class Employee(BaseModel, Base):
    """
    """
    __tablename__ = "employees"

    first_name = mapped_column(String(200), nullable=False)
    middle_name = mapped_column(String(200))
    last_name = mapped_column(String(200), nullable=False)
    home_address = mapped_column(String(300), nullable=False)
    role = mapped_column(String(200), nullable=False)
    is_admin = mapped_column(Boolean, default=False)
