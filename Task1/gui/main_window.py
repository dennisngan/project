from datetime import datetime

from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QScrollArea, \
    QGridLayout, QLineEdit, QTableWidget, QHeaderView, QStackedWidget, QMessageBox, QTableWidgetItem, QSizePolicy, \
    QDialog

from constant.constants import ROLE_EMOJI
from database.db_manager import DatabaseManager
from gui.dialogs.payment_dialog import PaymentDialog
from gui.dialogs.receipt_dialog import ReceiptDialog
from gui.styles import Colors, StyleEngine
from gui.widgets.product_card import ProductCard
from models.category import Category
from models.product import Product
from models.receipt import Receipt
from models.user import User
from services.cart_service import Cart
from services.category_cache import CategoryCache
from services.product_service import ProductService
from services.transaction_service import TransactionService


class MainWindow(QMainWindow):
    open_manager_panel = Signal()
    logout_requested = Signal()

    def __init__(self, user: User, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self._user = user
        self._db = db
        self._cart = Cart()
        self.product_service = ProductService(db)
        self.transaction_service = TransactionService(db)
        self._active_category: int = 0  # 0 means "All"
        self._category_buttons: dict[int | None, QPushButton] = {}
        self._products_cache: list[Product] = []
        self.refresh_products_cache()
        self._setup_ui()
        self._start_clock()
        self._load_products()
        self._update_status(len(self._products_cache))

    def _setup_ui(self):
        self.setWindowTitle("Quick Store - POS System")
        self.setFixedSize(1300, 880)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        root.addWidget(self._build_top_bar())

        # Content area
        content = QHBoxLayout()
        content.setContentsMargins(12, 12, 12, 12)
        content.setSpacing(12)
        content.addWidget(self._build_product_panel(), stretch=10)
        content.addWidget(self._build_cart_panel(), stretch=5)
        root.addLayout(content)

    # ── UI construction ─────────────────────────────────────────────────────────
    def _build_top_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.BG_SURFACE};
                border-bottom: 1px solid {Colors.BORDER};
            }}
            QFrame > QLabel {{
                background: transparent;
                border: none;
            }}
            #logo {{
                color: {Colors.TEXT}; font-size: 15px; font-weight: bold;
            }}
            #separator {{
                color: {Colors.BORDER_STRONG}; font-size: 14px;
            }}
            #pos_label {{
                color: {Colors.TEXT_MUTED}; font-size: 13px;
            }}
            #userInfo {{
                background-color: #E8E8ED;
                border-radius: 8px;
                border: 0.5px solid rgba(0, 0, 0, 0.12);
            }}
            #userNameLabel {{
                background-color: transparent;
                color: {Colors.TEXT}; font-size: 14px; font-weight: 600;
            }}
            #userRoleLabel {{
                background-color: transparent;
                color: {Colors.TEXT_GREY}; font-size: 10px;
            }}
            """
        )
        bar.setFixedHeight(56)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # App accent dot
        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(
            f"background-color: {Colors.STATUS_ONLINE}; border-radius: 5px; "
            f"min-width: 10px; min-height: 10px; border: none;"
        )
        layout.addWidget(dot)

        logo = QLabel("🏪 Quick Store")
        logo.setObjectName("logo")
        layout.addWidget(logo)

        sep = QLabel("|")
        sep.setObjectName("separator")
        layout.addWidget(sep)

        pos_lbl = QLabel("POS System")
        pos_lbl.setObjectName("pos_label")
        layout.addWidget(pos_lbl)
        layout.addStretch()

        # User info
        user_info = QWidget()
        user_info.setObjectName("userInfo")

        user_layout = QVBoxLayout(user_info)
        user_layout.setContentsMargins(10, 0, 10, 0)
        user_layout.setSpacing(0)

        user_layout.addStretch()

        name_label = QLabel(f"👤  {self._user.full_name}")
        name_label.setObjectName("userNameLabel")

        role_emoji = ROLE_EMOJI.get(self._user.role, "")
        role_label = QLabel(f'({role_emoji} {self._user.role.value.capitalize()})')
        role_label.setObjectName("userRoleLabel")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        user_layout.addWidget(name_label)
        user_layout.addWidget(role_label)
        user_layout.addStretch()

        layout.addWidget(user_info)

        # Clock
        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px; border: none;")
        layout.addWidget(self._clock_lbl)

        mgr_btn = QPushButton(f'⚙️ {self._user.role.value.capitalize()} Panel')
        mgr_btn.setCursor(Qt.PointingHandCursor)
        mgr_btn.clicked.connect(self.open_manager_panel.emit)
        layout.addWidget(mgr_btn)

        logout_btn = QPushButton("⏻ Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setProperty("danger", "true")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

        return bar

    def _build_product_panel(self) -> QWidget:
        panel = QFrame()
        panel.setProperty("card", True)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Search bar
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(" 🔍  Search by product ID or name...")
        self._search_input.setMinimumHeight(30)
        self._search_input.setStyleSheet(
            f"border-radius: 10px; font-size: 13px; "
            f"background-color: {Colors.BG_INPUT}; border: 1px solid {Colors.BORDER_STRONG};"
        )
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._load_products)
        self._search_input.textChanged.connect(lambda: self._search_timer.start())
        layout.addWidget(self._search_input)

        # Category filter pills
        self._cat_bar_layout = QHBoxLayout()
        self._cat_bar_layout.setSpacing(6)
        self._cat_bar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self._cat_bar_layout)

        # Product scroll area
        self._product_scroll = QScrollArea()
        self._product_scroll.setProperty("scrollbar", True)
        self._product_scroll.setWidgetResizable(True)
        self._product_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._product_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self._product_grid_widget = QWidget()
        self._product_grid = QGridLayout(self._product_grid_widget)
        self._product_grid.setSpacing(10)
        self._product_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._product_scroll.setWidget(self._product_grid_widget)

        layout.addWidget(self._product_scroll)
        return panel

    def _build_cart_panel(self) -> QWidget:
        panel = QFrame()
        panel.setProperty("card", True)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header row with item count badge
        header_row = QHBoxLayout()
        header = QLabel("Order")
        header.setStyleSheet(
            f"color: {Colors.TEXT}; font-size: 15px; font-weight: bold;"
        )
        header_row.addWidget(header)
        header_row.addStretch()

        self._order_count_badge = QLabel("0")
        self._order_count_badge.setStyleSheet(
            f"background-color: {Colors.ACCENT}; color: {Colors.TEXT_ON_ACCENT}; "
            f"font-size: 12px; font-weight: bold; padding: 2px 8px; border-radius: 10px;"
        )
        self._order_count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_row.addWidget(self._order_count_badge)
        layout.addLayout(header_row)

        # Cart table
        self._cart_table = QTableWidget()
        self._cart_table.setColumnCount(5)
        self._cart_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._cart_table.setHorizontalHeaderLabels(["Item", "Qty", "−", "+", "Total"])
        self._cart_table.setAlternatingRowColors(True)
        self._cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._cart_table.setColumnWidth(1, 45)
        self._cart_table.setColumnWidth(2, 45)
        self._cart_table.setColumnWidth(3, 45)
        self._cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._cart_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._cart_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self._cart_table.verticalHeader().setVisible(False)
        self._cart_table.verticalHeader().setDefaultSectionSize(40)

        # Empty cart label
        self._empty_label = QLabel("Add products to begin")
        self._empty_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 13px;")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Stack: page 0 = empty label, page 1 = cart table
        # Keeps consistent layout size regardless of cart state
        self._cart_stack = QStackedWidget()
        self._cart_stack.addWidget(self._empty_label)  # index 0
        self._cart_stack.addWidget(self._cart_table)  # index 1
        layout.addWidget(self._cart_stack, stretch=1)

        # Totals section — elevated card
        totals_frame = QFrame()
        totals_frame.setStyleSheet(
            f"background-color: {Colors.BG_SURFACE}; border-radius: 12px; "
        )
        totals_layout = QVBoxLayout(totals_frame)
        totals_layout.setContentsMargins(16, 14, 16, 14)
        totals_layout.setSpacing(8)

        def total_row(label: str, value_attr: str, large: bool = False) -> QLabel:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFont(StyleEngine.get_mono_font())
            lbl.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px; background: transparent;")
            val = QLabel("HKD $0.0")
            style = (
                f"color: {Colors.ACCENT}; font-size: 20px; font-weight: bold; background: transparent;"
                if large else
                f"color: {Colors.TEXT}; font-size: 13px; background: transparent;"
            )
            val.setStyleSheet(style)
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            totals_layout.addLayout(row)
            setattr(self, value_attr, val)
            return val

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {Colors.BORDER};")
        totals_layout.addWidget(div)

        total_row("Total:", "_total_lbl", large=True)
        layout.addWidget(totals_frame)

        # Pay button — full width, prominent
        pay_btn = QPushButton("Pay")
        pay_btn.setFixedHeight(38)
        pay_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pay_btn.clicked.connect(self._on_pay_btn_clicked)
        layout.addWidget(pay_btn)

        # Clear button — full width, secondary
        clear_btn = QPushButton("Clear Cart")
        clear_btn.setProperty("danger", True)
        clear_btn.setFixedHeight(38)
        clear_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        clear_btn.clicked.connect(self._on_cart_clear)
        layout.addWidget(clear_btn)

        return panel

    # ── UI construction ─────────────────────────────────────────────────────────

    # ─── Product loading and filtering ───────────────────────────────────────────────
    def _load_products(self):
        # Rebuild category pills if first load
        if not self._category_buttons:
            self._build_category_pills()

        # Clear existing products
        while self._product_grid.count():
            item = self._product_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered_products = self._get_filtered_products()

        if not filtered_products:
            empty = QLabel("No products found")
            empty.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 12px; padding: 20px;")
            self._product_grid.addWidget(empty, 0, 0)
            self._update_status(len(filtered_products))
            return

        cols = 5
        for col in range(cols):
            self._product_grid.setColumnStretch(col, 1)

        for i, p in enumerate(filtered_products):
            card = ProductCard(p)
            card.clicked.connect(self._on_product_clicked)
            self._product_grid.addWidget(card, i // cols, i % cols)

        self._update_status(len(filtered_products))

    def refresh_products_cache(self):
        """Reload products from the database and refresh the UI."""
        self._products_cache = self.product_service.get_all_products()

    def _get_filtered_products(self) -> list[Product]:
        """Apply current search and category filters to the products cache."""
        filtered = self._products_cache

        if self._active_category != 0:
            filtered = [p for p in filtered if p.category_id == self._active_category]

        query = self._search_input.text().strip().lower() if hasattr(self, "_search_input") else ""
        if query:
            filtered = [
                p for p in filtered
                if query in p.name.lower() or query in str(p.product_id)
            ]

        return filtered

    def _build_category_pills(self):
        """Build 'All' + one pill per category."""
        # Clear existing
        while self._cat_bar_layout.count():
            item = self._cat_bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        categories: list[Category] = [Category.all()] + (list(CategoryCache.get_map().values()))
        for cat in categories:
            category_id, name = cat.category_id, cat.name
            btn = QPushButton(name)
            btn.setProperty("category_active" if category_id == self._active_category else "category", True)
            btn.clicked.connect(lambda checked, cid=category_id: self._on_category_filter(cid))
            self._cat_bar_layout.addWidget(btn)
            self._category_buttons[category_id] = btn
        self._cat_bar_layout.addStretch()

    def _on_category_filter(self, category_id: int | None):
        self._active_category = category_id
        # Update pill styles
        for cid, btn in self._category_buttons.items():
            btn.setProperty("category_active", cid == category_id)
            btn.setProperty("category", cid != category_id)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._load_products()

    # ─── Product loading and filtering ───────────────────────────────────────────────

    # ── Cart management ─────────────────────────────────────────────────────────
    def _on_product_clicked(self, product_id: int):
        product: Product = next(filter(lambda p: p.product_id == product_id, self._products_cache), None)

        if product is None:
            return
        cart_item = self._cart.get_item(product_id)
        current_qty = cart_item.quantity if cart_item else 0
        if current_qty >= product.stock_quantity:
            QMessageBox.warning(self, "Out of Stock",
                                f"Only {product.stock_quantity} of {product.name} in stock.")
            return
        self._cart.add_item(product_id, product.name, product.price, product.category_id, 1, )
        self._refresh_cart_table()

    def _refresh_cart_table(self):
        items = self._cart.get_items()
        self._cart_table.setRowCount(0)

        self._cart_stack.setCurrentIndex(0 if self._cart.is_empty() else 1)

        # Update order count badge
        self._order_count_badge.setText(str(len(items)))

        for item in items:
            r = self._cart_table.rowCount()
            self._cart_table.insertRow(r)

            name_item = QTableWidgetItem(item.name[:30])
            qty_item = QTableWidgetItem(str(item.quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item = QTableWidgetItem(f"HKD${item.line_total:>7.1f}")
            total_item.setFont(StyleEngine.get_mono_font())
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self._cart_table.setItem(r, 0, name_item)
            self._cart_table.setItem(r, 1, qty_item)

            # − button
            minus_btn = QPushButton("−")
            minus_btn.setObjectName("cartMinusBtn")
            minus_btn.setFixedSize(26, 26)
            minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            minus_btn.setStyleSheet("""
            QPushButton#cartMinusBtn {
                background-color: #FFE5E5;
                color: #FF3B30;
                border: none;
                border-radius: 13px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                min-width: 26px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
                outline: none;
            }
            QPushButton#cartMinusBtn:hover { background-color: #FFCDD2; }
            QPushButton#cartMinusBtn:pressed { background-color: #FF3B30; color: #ffffff; }
        """)
            minus_btn.clicked.connect(
                lambda _, pid=item.product_id: (self._cart.update_quantity(pid, -1), self._refresh_cart_table()))

            minus_container = QWidget()
            minus_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            minus_container.setStyleSheet("background: transparent; border: none; padding: 0px; margin: 0px;")
            minus_lay = QHBoxLayout(minus_container)
            minus_lay.setContentsMargins(0, 0, 0, 0)
            minus_lay.setSpacing(0)
            minus_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            minus_lay.addWidget(minus_btn)
            self._cart_table.setCellWidget(r, 2, minus_container)

            # + button
            plus_btn = QPushButton("+")
            plus_btn.setObjectName("cartPlusBtn")
            plus_btn.setFixedSize(26, 26)
            plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            plus_btn.setStyleSheet("""
            QPushButton#cartPlusBtn {
                background-color: #E5F1FF;
                color: #007AFF;
                border: none;
                border-radius: 13px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                min-width: 26px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
                outline: none;
            }
            QPushButton#cartPlusBtn:hover { background-color: #CCE4FF; }
            QPushButton#cartPlusBtn:pressed { background-color: #007AFF; color: #ffffff; }
        """)
            plus_btn.clicked.connect(
                lambda _, pid=item.product_id: self._on_cart_increment(pid)
            )

            plus_container = QWidget()
            plus_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            plus_container.setStyleSheet("background: transparent; border: none; padding: 0px; margin: 0px;")
            plus_lay = QHBoxLayout(plus_container)
            plus_lay.setContentsMargins(0, 0, 0, 0)
            plus_lay.setSpacing(0)
            plus_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            plus_lay.addWidget(plus_btn)
            self._cart_table.setCellWidget(r, 3, plus_container)
            self._cart_table.setItem(r, 4, total_item)
        self._update_total()

    def _on_cart_increment(self, product_id: int):
        product: Product = next(filter(lambda p: p.product_id == product_id, self._products_cache), None)
        if product is None:
            return
        cart_item = self._cart.get_item(product_id)
        current_qty = cart_item.quantity if cart_item else 0
        if current_qty >= product.stock_quantity:
            QMessageBox.warning(self, "Out of Stock",
                                f"Only {product.stock_quantity} of {product.name} in stock.")
            return
        self._cart.update_quantity(product_id, +1)
        self._refresh_cart_table()

    def _on_cart_clear(self):
        self._cart.clear()
        self._refresh_cart_table()

    def _update_total(self):
        self._total_lbl.setText(f"${self._cart.get_total():.2f}")

    def _on_pay_btn_clicked(self):
        if self._cart.is_empty():
            QMessageBox.information(self, "Cart is empty", "Please add items to the cart before proceeding to payment.")
            return

        total_amount = self._cart.get_total()
        dialog = PaymentDialog(total_amount, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        payment = dialog.payment_method

        if payment is None:
            return

        tx_id = self.transaction_service.save_transaction(
            self._user.user_id,
            self._cart,
            payment
        )

        transaction = self.transaction_service.get_transaction(tx_id)

        receipt = Receipt(transaction)
        receipt_dialog = ReceiptDialog(str(receipt), transaction.transaction_id)
        receipt_dialog.exec()

        self._cart.clear()
        self._refresh_cart_table()
        self.refresh_products_cache()  # Refresh stock levels after sale
        self._load_products()

    # Status bar
    def _update_status(self, count: int = 0):
        self.statusBar().showMessage(
            f"  Products: {count}  available"
        )

    # Clock
    def _start_clock(self):
        self._update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1_000)  # Update every second

    def _update_clock(self):
        now = datetime.now().strftime("%b %d, %Y  %H:%M:%S")
        self._clock_lbl.setText(f"🕐 {now}")
