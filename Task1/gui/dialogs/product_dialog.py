from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QFrame, QSpinBox, QDoubleSpinBox, )

from gui.styles import Colors
from models.product import Product
from services.category_cache import CategoryCache
from utils.validators import Validators


class ProductDialog(QDialog):
    """
    Dialog for adding or editing a product.
    If initialized with an existing Product, it will be in "edit" mode and pre-fill the form.
    Otherwise, it's in "add" mode with empty form.
    """

    def __init__(self, product: Product | None = None, parent=None):
        super().__init__(parent)
        self._source = product
        self._result_product: Product | None = None
        self._setup_ui()
        if product:
            self._populate(product)

    @property
    def result_product(self) -> Product | None:
        return self._result_product

    # ── UI construction ─────────────────────────────────────────────────────────

    def _setup_ui(self):
        title = "Edit Product" if self._source else "Add Product"
        self.setWindowTitle(title)
        self.setFixedSize(450, 480)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(32, 32, 32, 32)

        # Header
        header = QLabel(title)
        header.setStyleSheet(
            f"font-size: 17px; font-weight: bold; color: {Colors.TEXT};"
        )
        layout.addWidget(header)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {Colors.BORDER};")
        layout.addWidget(divider)

        # Form
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: 500;"
            )
            return l

        # Name
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("e.g. Coca-Cola 355ml")
        self._name_input.setMinimumHeight(38)
        form.addRow(lbl("Name *"), self._name_input)

        # Price
        self._price_spin = QDoubleSpinBox()
        self._price_spin.setPrefix("HKD$ ")
        self._price_spin.setDecimals(2)
        self._price_spin.setRange(0, 9999.9)
        self._price_spin.setMinimumHeight(38)
        form.addRow(lbl("Price *"), self._price_spin)

        # Cost Price
        self._cost_spin = QDoubleSpinBox()
        self._cost_spin.setPrefix("HKD$ ")
        self._cost_spin.setDecimals(2)
        self._cost_spin.setRange(0, 9999.9)
        self._cost_spin.setMinimumHeight(38)
        form.addRow(lbl("Cost Price *"), self._cost_spin)

        # Stock
        self._stock_spin = QSpinBox()
        self._stock_spin.setRange(0, 99999)
        self._stock_spin.setMinimumHeight(38)
        form.addRow(lbl("Stock Qty *"), self._stock_spin)

        # Category
        self._cat_combo = QComboBox()
        self._cat_combo.setMinimumHeight(38)

        for key, value in CategoryCache.get_map().items():
            self._cat_combo.addItem(value.name, key)

        form.addRow(lbl("Category"), self._cat_combo)
        layout.addLayout(form)

        # Error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet(f"color: {Colors.DANGER}; font-size: 11px;")
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("secondary", True)
        cancel_btn.clicked.connect(self.reject)

        _save_btn = QPushButton("Save Product")
        _save_btn.setMinimumHeight(44)
        _save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(_save_btn)
        layout.addLayout(btn_row)

    def _populate(self, p: Product):
        """Pre-fill form with existing product data."""
        self._name_input.setText(p.name)
        self._price_spin.setValue(p.price)
        self._cost_spin.setValue(p.cost_price)
        self._stock_spin.setValue(p.stock_quantity)
        self._cat_combo.setCurrentIndex(self._cat_combo.findData(p.category_id))

    def _on_save(self):
        """Validate and build the Product object."""
        name = self._name_input.text().strip()
        price = self._price_spin.value()
        cost = self._cost_spin.value()
        stock = self._stock_spin.value()
        cat_id = self._cat_combo.currentData()

        if not Validators.is_valid_product_name(name):
            self._show_error("Product name is required (1–100 characters).")
            return
        if not Validators.is_valid_price(price):
            self._show_error("Price must be 0 or more.")
            return
        if not Validators.is_valid_stock(stock):
            self._show_error("Stock must be non-negative integer.")
            return

        pid = self._source.product_id if self._source else 0

        product = Product(
            product_id=pid, name=name, price=price,
            cost_price=cost, stock_quantity=stock, category_id=cat_id,
        )

        self._result_product = product
        self._error_label.hide()
        self.accept()

    def _show_error(self, msg: str):
        self._error_label.setText(f"⚠  {msg}")
        self._error_label.show()
