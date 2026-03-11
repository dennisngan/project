import sqlite3
from datetime import datetime
from typing import Self

from models.base import BaseModel
from models.payment_method import PaymentMethod


class Transaction(BaseModel):
    """
    Represents a completed transaction in the POS system. Contains details about the transaction, including:
    - transaction_id: Unique identifier for the transaction
    - timestamp: Date and time when the transaction occurred
    - cashier_id: ID of the cashier who processed the transaction
    - cashier_name: Name of the cashier (for easier reporting)
    - items: List of items sold in the transaction (snapshots of CartItem)
    - total_amount: Total amount of the transaction
    - payment: PaymentMethod instance representing how the transaction was paid
    """

    @classmethod
    def from_db_row(cls, row: sqlite3.Row) -> Self:
        pass

    def __init__(
            self,
            transaction_id: int,
            timestamp: str,
            cashier_id: int,
            cashier_name: str,
            items: list,  # list[CartItem] snapshots
            total_amount: float,
            payment: PaymentMethod,
    ):
        super().__init__()
        self.transaction_id = transaction_id
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cashier_id = cashier_id
        self.cashier_name = cashier_name
        self.items = list(items)
        self.total_amount = total_amount
        self.payment = payment

    def validate(self) -> bool:
        return self.total_amount >= 0 and len(self.items) > 0

    def __str__(self) -> str:
        return (
            f"Transaction #{self.transaction_id} | "
            f"{self.timestamp} | "
            f"Total: ${self.total_amount:.2f} | "
            f"{self.payment}"
        )

    def __repr__(self) -> str:
        return f"<Transaction id={self.transaction_id} total={self.total_amount:.2f}>"
