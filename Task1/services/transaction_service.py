from __future__ import annotations

from database.db_manager import DatabaseManager
from models.transaction import PaymentMethod
from services.cart_service import Cart
from services.product_service import ProductService


class TransactionService:
    """Handles transaction persistence and related business logic."""

    def __init__(self, db: DatabaseManager):
        self._db = db
        self._product_service = ProductService(db)

    def save_transaction(self, cashier_id: int, cart: Cart, payment: PaymentMethod) -> int:
        """
            Save the transaction header and line items to the database.
        Args:
            cashier_id (): ID of the cashier processing the sale.
            cart (): Cart object containing the items being purchased.
            payment (): PaymentMethod object with payment details.
        Returns:
                int: The new transaction ID.
        """

        try:
            """ Insert transaction header and get new transaction ID."""
            self._db.execute(
                """INSERT INTO transactions (cashier_id,
                                             total_amount,
                                             payment_type,
                                             amount_tendered,
                                             change_due,
                                             card_last_four)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    cashier_id,
                    cart.get_total(),
                    payment.payment_type.value,
                    payment.amount_tendered,
                    payment.change_due,
                    payment.card_number_last4
                ),
            )
            tx_id = self._db.get_last_insert_id()

            """ Insert line items and update stock in a single transaction. """
            for item in cart.get_items():
                self._db.execute(
                    """INSERT INTO transaction_items (transaction_id,
                                                      product_id,
                                                      quantity,
                                                      unit_price,
                                                      line_total)
                       VALUES (?, ?, ?, ?, ?)""",
                    (tx_id,
                     item.product_id,
                     item.quantity,
                     item.unit_price,
                     item.line_total
                     ),
                )
                self._product_service.update_stock(item.product_id, item.quantity)

            self._db.commit()
        except Exception:
            self._db.rollback()
            raise
        return tx_id

    def void_transaction(self, transaction_id: int) -> None:
        """Mark a transaction as voided."""
        self._db.execute(
            "UPDATE transactions SET is_void = 1 WHERE id = ?",
            (transaction_id,),
        )
        self._db.commit()
