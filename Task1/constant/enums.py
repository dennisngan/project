"""
Application-wide enumeration types.

Both enums inherit from (str, Enum), a form of multiple inheritance that makes each
enum value directly usable as a plain string (e.g. in SQLite queries) while still
providing the type-safety and membership checks of a standard Enum.
"""

from enum import Enum


class UserRole(str, Enum):
    MANAGER = "manager"
    CASHIER = "cashier"


class PaymentType(str, Enum):
    CASH = "cash"
    CARD = "card"
