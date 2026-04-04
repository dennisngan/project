from __future__ import annotations

from database.db_manager import DatabaseManager
from models.transaction import PaymentMethod, Transaction
from models.transaction_item import TransactionItem
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
                product = self._product_service.get_product_by_id(item.product_id)
                if product is None:
                    raise ValueError(f"Product ID {item.product_id} ('{item.name}') no longer exists.")
                self._db.execute(
                    """INSERT INTO transaction_items (transaction_id,
                                                      product_id,
                                                      product_name,
                                                      quantity,
                                                      unit_price,
                                                      line_total)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (tx_id,
                     product.product_id,
                     product.name,
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
    def get_all_transactions(self, limit: int = 50) -> list[Transaction]:
        """Return a list of recent transactions with header details."""
        rows = self._db.fetchall(
            """SELECT *
               FROM transactions
               ORDER BY timestamp DESC
               LIMIT ?""",
            (limit,),
        )
        transactions = []

        for row in rows:
            transaction = Transaction.from_db_row(row)
            transactions.append(transaction)
            # Lazy load items only when needed to avoid overhead in the summary table
        return transactions

    def get_transaction(self, transaction_id: int) -> Transaction:
        """Return transaction header details for a given transaction ID."""
        row = self._db.fetchone(
            """SELECT *
               FROM transactions
               WHERE transaction_id = ?""",
            (transaction_id,),
        )
        transaction = Transaction.from_db_row(row) if row else None
        if not transaction:
            return None
        transaction.items = self.get_items_for_transaction(transaction_id)
        return transaction

    def get_items_for_transaction(self, transaction_id: int) -> list[TransactionItem]:
        rows = self._db.fetchall(
            """SELECT transaction_item_id,
                      transaction_id,
                      product_id,
                      product_name,
                      quantity,
                      unit_price,
                      line_total
               FROM transaction_items
               WHERE transaction_id = ?""",
            (transaction_id,),
        )
        return [TransactionItem.from_db_row(row) for row in rows]

    def void_transaction(self, transaction_id: int) -> None:
        """Mark a transaction as voided and restore deducted stock."""
        row = self._db.fetchone(
            "SELECT is_void FROM transactions WHERE transaction_id = ?",
            (transaction_id,),
        )
        if row is None:
            raise ValueError(f"Transaction {transaction_id} not found.")
        if row["is_void"]:
            raise ValueError(f"Transaction {transaction_id} is already voided.")
        try:
            items = self._db.fetchall(
                "SELECT product_id, quantity FROM transaction_items WHERE transaction_id = ?",
                (transaction_id,),
            )
            for item in items:
                self._db.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + ? WHERE product_id = ?",
                    (item["quantity"], item["product_id"]),
                )
            self._db.execute(
                "UPDATE transactions SET is_void = 1 WHERE transaction_id = ?",
                (transaction_id,),
            )
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise
