from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel

from config import LOW_STOCK_THRESHOLD
from gui.styles import StyleEngine, Colors
from models.product import Product
from utils.category_color import get_category_color


class ProductCard(QFrame):
    """
    Clickable product card widget displayed in the product grid.
    Emits clicked(product_id) when pressed.
    """
    clicked = Signal(int)  # product_id

    def __init__(self, product: Product, parent=None):
        super().__init__(parent)
        self._product = product
        self._setup_ui()

    def _setup_ui(self):
        cat_color = get_category_color(self._product)
        self.setStyleSheet(StyleEngine.product_card_stylesheet(cat_color))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(180)
        self.setFixedWidth(148)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        # Top row: name + category color dot
        top_row = QHBoxLayout()
        top_row.setSpacing(4)
        top_row.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(self._product.name)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(
            f"color: {Colors.TEXT}; font-size: 12px; font-weight: 600; background: transparent;"
        )
        top_row.addWidget(name_lbl, stretch=1)

        layout.addLayout(top_row)
        layout.addStretch()

        price_lbl = QLabel(f"HKD${self._product.price:.1f}")
        price_lbl.setStyleSheet(
            f"color: {Colors.ACCENT}; font-size: 14px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(price_lbl)

        # Stock badge — pill style for low stock
        if self._product.stock_quantity == 0:
            stock_text = f"#{self._product.product_id} · Out of Stock"
            stock_style = (
                f"color: {Colors.DANGER}; background-color: {Colors.DANGER_LIGHT}; "
                f"font-size: 10px; border-radius: 6px; padding: 1px 6px; background: transparent;"
            )
        elif self._product.stock_quantity <= LOW_STOCK_THRESHOLD:
            stock_text = f"#{self._product.product_id} · Low: {self._product.stock_quantity}"
            stock_style = (
                f"color: {Colors.DANGER}; font-size: 10px; background: transparent;"
            )
        else:
            stock_text = f"#{self._product.product_id} · {self._product.stock_quantity} in stock"
            stock_style = f"color: {Colors.TEXT_MUTED}; font-size: 10px; background: transparent;"

        meta_lbl = QLabel(stock_text)
        meta_lbl.setStyleSheet(stock_style)
        layout.addWidget(meta_lbl)

    # Mouse events for click feedback and effects. We use mousePressEvent and mouseReleaseEvent to allow for "pressed" visual state.
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._product.stock_quantity > 0:
                self._set_pressed(True)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._set_pressed(False)
            if self._product.stock_quantity > 0:
                self.clicked.emit(self._product.product_id)
        super().mouseReleaseEvent(event)

    def _set_pressed(self, pressed: bool):
        cat_color = get_category_color(self._product)
        if pressed:
            self.setStyleSheet(StyleEngine.product_card_stylesheet(cat_color) + """
                QFrame {
                    transform: scale(0.97);
                    opacity: 0.85;
                    border: 2px solid rgba(0,0,0,0.18);
                    background-color: rgba(0,0,0,0.06);
                }
            """)
        else:
            self.setStyleSheet(StyleEngine.product_card_stylesheet(cat_color))
