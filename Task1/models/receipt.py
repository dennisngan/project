from config import STORE_NAME, STORE_ADDRESS, STORE_PHONE
from models.transaction import Transaction


class Receipt:
    """
    Generates a formatted text receipt from a completed Transaction.
    """

    WIDTH = 42  # Characters wide (thermal receipt style)

    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    @staticmethod
    def format_line(left: str, right: str, width: int = 42) -> str:
        """Right-align *right* within *width* chars, left-justify *left*."""
        gap = width - len(left) - len(right)
        if gap < 1:
            gap = 1
        return left + " " * gap + right

    @staticmethod
    def divider(char: str = "─", width: int = 42) -> str:
        return char * width

    def build(self) -> str:
        """Assemble and return the full receipt as a string."""
        w = self.WIDTH
        transaction = self.transaction
        payment = self.transaction.payment
        lines: list[str] = list()

        # Header
        lines.append(self.divider("═", w))
        lines.append(STORE_NAME.center(w))
        lines.append(STORE_ADDRESS.center(w))
        lines.append(STORE_PHONE.center(w))
        lines.append(self.divider("═", w))
        lines.append(f"Receipt #{transaction.transaction_id}".center(w))
        lines.append(transaction.timestamp.center(w))
        cashier_label = f"ID #{transaction.cashier_id}"
        lines.append(f"Cashier: {cashier_label}".center(w))
        lines.append(self.divider("─", w))

        # Items
        lines.append(f"{'Item':<16}{'Qty':>4}  {'Price':>9}  {'Total':>9}")
        lines.append(self.divider("─", w))
        for item in transaction.items:
            name = item.product_name[:16]
            price_str = f"HKD${item.unit_price:.1f}"
            total_str = f"HKD${item.line_total:.1f}"
            lines.append(
                f"{name:<16}{item.quantity:>4}  {price_str:>9}  {total_str:>9}"
            )

        # Totals
        lines.append(self.divider("─", w))
        lines.append(self.format_line("  TOTAL:", f"HKD${payment.total_amount:.1f}", w))

        # Payment details
        lines.append(self.divider("─", w))
        ptype = payment.payment_type.upper()
        lines.append(self.format_line("  Payment:", ptype, w))
        if payment.amount_tendered is not None:
            lines.append(self.format_line("  Tendered:", f"HKD${payment.amount_tendered:.1f}", w))
            lines.append(self.format_line("  Change:", f"HKD${payment.change_due:.1f}", w))
        elif payment.card_number_last4 is not None:
            lines.append(self.format_line("  Card:", f"****{payment.card_number_last4}", w))

        # Footer
        lines.append(self.divider("═", w))
        lines.append("Thank you for shopping at".center(w))
        lines.append(STORE_NAME.center(w))
        lines.append(self.divider("─", w))

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.build()

    def __repr__(self) -> str:
        return f"<Receipt transaction_id={self.transaction.transaction_id}>"


if __name__ == "__main__":
    # Minimal smoke test
    from models.transaction import Transaction
    from models.payment_method import CashPayment
    from models.transaction_item import TransactionItem

    cash = CashPayment(total_amount=13.55, amount_tendered=20.00, change_due=6.45)
    cash.process_payment()

    items = [
        TransactionItem(1, 42, 1, "Coca-Cola 355ml", 2, 10.0, 20.0),
        TransactionItem(2, 42, 6, "Lay's Classic", 1, 14.5, 14.5),
    ]
    tx = Transaction(
        transaction_id=42,
        timestamp="2026-03-04 14:30:00",
        cashier_id=1,
        items=items,
        payment=cash,
        is_void=False,
    )
    receipt = Receipt(tx)
    print(receipt)
