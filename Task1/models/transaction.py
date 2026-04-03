import sqlite3
from datetime import datetime
from typing import Self

from constant.enums import PaymentType
from models.base import BaseModel
from models.payment_method import PaymentMethod, CashPayment, CardPayment
from models.transaction_item import TransactionItem


class Transaction(BaseModel):
    """
    Represents a completed sale transaction.
    Immutable record created after payment is successful.
    """
    def __init__(
            self,
            transaction_id: int,
            timestamp: str,
            cashier_id: int,
            payment: PaymentMethod,
            items: list[TransactionItem],  # list[CartItem] snapshots
            is_void: bool
    ):
        super().__init__()
        self.transaction_id = transaction_id
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cashier_id = cashier_id
        self.payment = payment
        self.items = list(items)
        self.is_void = is_void

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> Self:
        """
        Polymorphic factory: reconstructs a Transaction from a DB row.
        Selects the concrete PaymentMethod subclass (CardPayment or CashPayment)
        based on the payment_type column — demonstrating runtime polymorphism.
        Items are loaded separately because they require a JOIN query (lazy loading).
        """
        payment_type = row["payment_type"]
        total_amount = row["total_amount"]
        change_due = row["change_due"]
        payment: PaymentMethod | None = None
        if payment_type == PaymentType.CARD:
            payment = CardPayment(total_amount, row["card_last_four"] or "")
        elif payment_type == PaymentType.CASH:
            amount_tendered = row["amount_tendered"]
            payment = CashPayment(total_amount, amount_tendered, change_due)
        return cls(
            transaction_id=row["transaction_id"],
            timestamp=row["timestamp"],
            cashier_id=row["cashier_id"],
            payment=payment,
            items=[],
            is_void=row["is_void"] == 1,
        )

    def __str__(self) -> str:
        return (
            f"Transaction #{self.transaction_id} | "
            f"{self.timestamp} | "
            f"Total: ${self.payment.total_amount:.1f} | "
            f"{self.payment}"
        )

    def __repr__(self) -> str:
        return f"<Transaction id={self.transaction_id} total={self.payment.total_amount:.1f}>"
