from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QDialog, QPushButton, QHBoxLayout, QLabel, QFrame, QLineEdit, QStackedWidget

from gui.styles import Colors, StyleEngine
from gui.widgets.hkd_line_edit import HKDLineEdit
from models.payment_method import PaymentMethod, CashPayment, CardPayment


class PaymentDialog(QDialog):
    def __init__(self, total_amount: float, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 520)
        self.total_amount = total_amount
        self._payment_method: PaymentMethod | None = None
        self._setup_ui()

    @property
    def payment_method(self) -> PaymentMethod | None:
        return self._payment_method

    def _setup_ui(self):
        self.setWindowTitle("Payment")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        # Header
        header = QLabel("Payment")
        header.setFixedHeight(28)
        header.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {Colors.TEXT};"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Amount display — card with accent-light background
        amount_frame = QFrame()
        amount_frame.setFixedHeight(120)
        amount_frame.setStyleSheet(
            f"background-color: {Colors.ACCENT_LIGHT}; border-radius: 12px; border: none;"
        )
        amount_layout = QVBoxLayout(amount_frame)
        amount_layout.setContentsMargins(20, 20, 20, 20)
        amount_layout.setSpacing(4)

        total_label = QLabel(f"${self.total_amount:.1f}")
        total_label.setFixedHeight(48)
        total_label.setFont(StyleEngine.get_mono_font())
        total_label.setStyleSheet(
            f"font-size: 40px; font-weight: bold; color: {Colors.ACCENT}; background: transparent;"
        )
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_layout.addWidget(total_label)

        due_label = QLabel("Total Due")
        due_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        due_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_layout.addWidget(due_label)

        layout.addWidget(amount_frame)

        # Segmented control for Cash / Card
        toggle_container = QFrame()
        toggle_container.setFixedHeight(44)
        toggle_container.setStyleSheet(
            "background-color: #E5E5EA; border-radius: 10px; border: none;"
        )
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(3, 3, 3, 3)
        toggle_layout.setSpacing(2)

        self._cash_btn = QPushButton("Cash")
        self._card_btn = QPushButton("Card")
        for btn in (self._cash_btn, self._card_btn):
            btn.setMinimumHeight(38)
            btn.setCheckable(True)
        self._cash_btn.setChecked(True)
        self._cash_btn.clicked.connect(self._switch_to_cash)
        self._card_btn.clicked.connect(self._switch_to_card)
        toggle_layout.addWidget(self._cash_btn)
        toggle_layout.addWidget(self._card_btn)
        layout.addWidget(toggle_container)

        # Cash section
        self._cash_frame = QFrame()
        self._cash_frame.setFixedHeight(180)
        # self._cash_frame.setStyleSheet("background: transparent; border: none;")
        cash_layout = QVBoxLayout(self._cash_frame)
        cash_layout.setContentsMargins(0, 0, 0, 0)
        cash_layout.setSpacing(8)

        tendered_label = QLabel("Amount Tendered:")
        tendered_label.setFixedHeight(20)
        tendered_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;"
        )
        cash_layout.addWidget(tendered_label)

        self._tendered_input = HKDLineEdit()
        # self._tendered_input.setFont(StyleEngine.get_mono_font())
        # self._tendered_input.setPlaceholderText("HKD$ 0.0")
        # self._tendered_input.setMinimumHeight(52)
        self._tendered_input.setStyleSheet(
            f"font-size: 22px; text-align: right; "
            f"background-color: {Colors.BG_INPUT}; border: 1px solid {Colors.BORDER_STRONG}; "
            f"border-radius: 8px; padding: 6px 12px;"
        )
        self._tendered_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._tendered_input.textChanged.connect(self._update_change)
        cash_layout.addWidget(self._tendered_input)

        self._change_label = QLabel("")
        self._change_label.setFont(StyleEngine.get_mono_font())
        self._change_label.setStyleSheet(
            f"color: {Colors.SUCCESS}; background-color: {Colors.SUCCESS_LIGHT}; "
            f"font-size: 18px; font-weight: bold; border-radius: 10px; padding: 20px 20px;"
        )
        self._change_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cash_layout.addWidget(self._change_label)
        cash_layout.addStretch()

        # Card section (hidden by default)
        self._card_frame = QFrame()
        self._card_frame.setFixedHeight(180)
        # self._card_frame.setStyleSheet("background: transparent; border: none;")
        card_inner = QVBoxLayout(self._card_frame)
        card_inner.setContentsMargins(0, 0, 0, 0)
        card_inner.setSpacing(8)

        card_num_label = QLabel("Last 4 digits of card:")
        card_num_label.setFixedHeight(20)
        card_num_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;"
        )
        card_inner.addWidget(card_num_label)

        self._card_input = QLineEdit()
        self._card_input.setPlaceholderText("e.g. 4242")
        self._card_input.setMaxLength(4)
        self._card_input.setMinimumHeight(52)
        self._card_input.setStyleSheet(
            f"font-size: 22px; "
            f"background-color: {Colors.BG_INPUT}; border: 1px solid {Colors.BORDER_STRONG}; "
            f"border-radius: 8px; padding: 6px 12px;"
        )
        self._card_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_inner.addWidget(self._card_input)
        card_inner.addStretch()

        self._payment_stack = QStackedWidget()
        self._payment_stack.setFixedHeight(180)
        self._payment_stack.setStyleSheet("background: transparent; border: none;")
        self._payment_stack.addWidget(self._cash_frame)  # index 0 = Cash
        self._payment_stack.addWidget(self._card_frame)  # index 1 = Card
        layout.addWidget(self._payment_stack)
        self._card_frame.hide()

        # Error label
        self._error_label = QLabel("")
        self._error_label.setWordWrap(True)
        self._error_label.setFixedHeight(45)
        self._error_label.setProperty("danger", True)
        self._error_label.setStyleSheet(
            f" font-size: 13px;"
        )
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sp = self._error_label.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self._error_label.setSizePolicy(sp)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.setFixedHeight(42)
        cancel_btn.clicked.connect(self.reject)  # Close dialog with cancel

        self._confirm_btn = QPushButton("Confirm")
        self._confirm_btn.setFixedHeight(42)
        self._confirm_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self._confirm_btn)
        layout.addLayout(btn_row)

        self._update_toggle_styles()

    def _update_change(self, text: str = ""):
        try:
            tendered = self._tendered_input.numeric_value()
            change = tendered - self.total_amount
            self._change_label.setFont(StyleEngine.get_mono_font())
            if change >= 0:
                self._change_label.setText(f"Change Due: HKD ${change:.1f}")
                self._change_label.setStyleSheet(
                    f"color: {Colors.SUCCESS}; background-color: {Colors.SUCCESS_LIGHT}; "
                    f"font-size: 18px; font-weight: bold; border-radius: 10px; padding: 20px 20px;"
                )
            else:
                self._change_label.setText(f"Remaining:  ${abs(change):.1f}")
                self._change_label.setStyleSheet(
                    f"color: {Colors.DANGER}; background-color: {Colors.DANGER_LIGHT}; "
                    f"font-size: 18px; font-weight: bold; border-radius: 10px; padding: 20px 20px;"
                )
        except ValueError:
            self._change_label.setText("Change Due: HKD $0.0")

    def _on_confirm(self):
        """Validate and build the appropriate PaymentMethod."""
        payment = None
        if self._cash_btn.isChecked():
            try:
                tendered = self._tendered_input.numeric_value()
                if tendered == 0.0 and self._tendered_input.text().strip() == HKDLineEdit.PREFIX.strip():
                    self._show_error("Please enter the amount tendered.")
                    return
                change_due = tendered - self.total_amount
                payment = CashPayment(self.total_amount, tendered, change_due)
                if not payment.process_payment():
                    self._show_error("Amount tendered is less than total due.")
                    return
            except ValueError:
                self._show_error("Please enter the amount tendered.")
                return
        elif self._card_btn.isChecked():
            digits_text = self._card_input.text().strip()

            if len(digits_text) != 4:
                self._show_error("Please enter exactly the LAST 4 digits from the card.")
                return

            try:
                str(int(digits_text))  # Ensure it's numeric and remove leading zeros
                payment = CardPayment(self.total_amount, digits_text)
                if not payment.process_payment():
                    self._show_error("Payment failed. Please check the card details and try again.")
                    return
            except ValueError:
                self._show_error("Please enter last 4 digits of the card.")
                return

        if payment is None:
            self.reject()
            return

        self._payment_method = payment
        self._error_label.hide()
        self.accept()  # Close dialog with success

    def _show_error(self, msg: str):
        self._error_label.setText(f"⚠  {msg}")
        self._error_label.show()

    def _switch_to_cash(self):
        self._error_label.setText("")
        self._cash_btn.setChecked(True)
        self._card_btn.setChecked(False)
        self._payment_stack.setCurrentIndex(0)
        self._update_toggle_styles()

    def _switch_to_card(self):
        self._error_label.setText("")
        self._cash_btn.setChecked(False)
        self._card_btn.setChecked(True)
        self._payment_stack.setCurrentIndex(1)
        self._update_toggle_styles()

    def _update_toggle_styles(self):
        active_style = (
            f"background-color: {Colors.BG_SURFACE}; color: {Colors.TEXT}; "
            f"border: 1px solid {Colors.BORDER}; border-radius: 8px; font-weight: bold;"
        )
        inactive_style = (
            f"background-color: transparent; color: {Colors.TEXT_MUTED}; "
            f"border: none; border-radius: 8px;"
        )
        self._cash_btn.setStyleSheet(active_style if self._cash_btn.isChecked() else inactive_style)
        self._card_btn.setStyleSheet(active_style if self._card_btn.isChecked() else inactive_style)
