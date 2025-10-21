#!/usr/bin/env python3

"""
Employee session model.
"""


from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from models.basemodel import BaseModel, Base


class EmployeeSession(BaseModel, Base):
    """Tracks active login sessions for employees."""

    __tablename__ = "employee_sessions"

    employee_id = mapped_column(
        String(36),
        ForeignKey("employees.id"),
        nullable=False
    )

    employee = relationship(
        "Employee",
        back_populates="employee_session"
    )
