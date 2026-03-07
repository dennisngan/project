from enum import Enum


class UserRole(str, Enum):
    MANAGER = "manager"
    CASHIER = "cashier"


class PaymentType(str, Enum):
    PAYMENT_CASH = "cash"
    PAYMENT_CARD = "card"


class Category(str, Enum):
    DRINK = "drinks"
    SNACKS = "snacks"
    BAKERY = "bakery"
    FROZEN = "frozen"
    HOUSEHOLD = "household"
    OTHER = "other"
