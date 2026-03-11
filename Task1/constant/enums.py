from enum import Enum


class UserRole(str, Enum):
    MANAGER = "manager"
    CASHIER = "cashier"


class PaymentType(str, Enum):
    CASH = "cash"
    CARD = "card"
