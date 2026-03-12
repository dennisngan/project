from abc import ABC, abstractmethod

from constant.enums import PaymentType


class PaymentMethod(ABC):
    """Abstract base for all payment strategies."""

    def __init__(self, total_amount: float):
        self.total_amount = total_amount
        self.amount_tendered: float | None = None
        self.change_due: float | None = None
        self.card_number_last4: str | None = None

    @abstractmethod
    def process_payment(self) -> bool:
        """Attempt to process the payment. Return True on success."""
        pass

    @property
    @abstractmethod
    def payment_type(self) -> PaymentType:
        """Return the type of payment method."""
        pass

    def __str__(self) -> str:
        return f"Payment[{self.payment_type}] | Total: ${self.total_amount:.2f}"


class CardPayment(PaymentMethod):
    """Concrete strategy for card payments."""
    PAYMENT_TYPE = PaymentType.CARD

    def __init__(self, total_amount: float, card_number_last4:str):
        super().__init__(total_amount)
        self.payment_gateway: str | None = "MOCK"
        self.card_number_last4 = card_number_last4
        self.payment_gateway_response: bool = False

    def process_payment(self) -> bool:
        """In a real implementation, this would call an external payment gateway API."""
        self.payment_gateway_response = True
        return self.payment_gateway_response

    @property
    def payment_type(self) -> PaymentType:
        return self.PAYMENT_TYPE

    def __str__(self) -> str:
        return (
            f"Card Payment | Total: ${self.total_amount:.1f} | "
            f"Card: **** **** **** {self.card_number_last4} | "
        )


class CashPayment(PaymentMethod):
    """Concrete strategy for cash payments."""
    PAYMENT_TYPE = PaymentType.CASH

    def __init__(self, total_amount: float, amount_tendered: float, change_due: float):
        super().__init__(total_amount)
        self.amount_tendered = amount_tendered
        self.change_due = change_due

    def process_payment(self) -> bool:
        if self.amount_tendered < self.total_amount:
            return False

        self.change_due = self.amount_tendered - self.total_amount
        return True

    @property
    def payment_type(self) -> PaymentType:
        return self.PAYMENT_TYPE

    def __str__(self) -> str:
        return (
            f"Cash Payment | Total: HKD${self.total_amount:.1f} | "
            f"Tendered: HKD${self.amount_tendered:.1f} | "
            f"Change: HKD${self.change_due:.1f}"
        )
