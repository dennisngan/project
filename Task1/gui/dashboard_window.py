from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QListWidget, QSplitter, QStackedWidget, QPushButton, \
    QHBoxLayout, QLineEdit, QTableWidget, QHeaderView, QSizePolicy, QDialog, QMessageBox, QLabel
from PySide6.QtWidgets import QTableWidgetItem

from config import STORE_NAME, LOW_STOCK_THRESHOLD
from constant.enums import PaymentType, UserRole
from database.db_manager import DatabaseManager
from gui.dialogs.product_dialog import ProductDialog
from gui.styles import Colors
from gui.widgets.top_bar import TopBar
from models.transaction import Transaction
from models.user import User
from services.category_cache import CategoryCache
from services.product_service import ProductService
from services.transaction_service import TransactionService
from services.user_service import UserService


class NumericTableItem(QTableWidgetItem):
    """QTableWidgetItem that sorts by numeric value, falling back to text."""

    def __lt__(self, other: QTableWidgetItem) -> bool:
        try:
            self_val = self.data(Qt.ItemDataRole.UserRole)
            other_val = other.data(Qt.ItemDataRole.UserRole)
            if self_val is not None and other_val is not None:
                return float(self_val) < float(other_val)
            # Fallback: strip currency prefix and parse
            return float(self.text().lstrip("HKD$")) < float(other.text().lstrip("HKD$"))
        except (ValueError, TypeError):
            return super().__lt__(other)


class DashboardWindow(QMainWindow):
    """
    Admin dashboard window providing product, transaction, and user management.

    Inherits from QMainWindow (Inheritance).  The sidebar is built dynamically based
    on the logged-in user's permissions (Role-Based Access Control), demonstrating
    Polymorphism: the same window renders differently for a Manager vs a Cashier.
    Static factory methods (_make_product_table, _make_summary_table, _make_users_table)
    encapsulate table construction so each tab is self-contained and reusable.
    """

    back_to_main_window = Signal()
    logout_requested = Signal()

    def __init__(self, user: User, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db
        self._user = user
        self._user_service = UserService(db)
        self._user_map: dict[int, User] = dict()
        self._product_service = ProductService(db)
        self._transaction_service = TransactionService(db)
        self._cache_user()
        self._setup_ui()

    def _cache_user(self):
        users = self._user_service.get_all_user()
        for user in users:
            self._user_map[user.user_id] = user

    # ── UI construction ─────────────────────────────────────────────────────────

    def _setup_ui(self):
        title = f"{STORE_NAME}'s Dashboard"
        self.setWindowTitle(title)
        self.setFixedSize(1300, 800)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_top_bar())

        # Sidebar + content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(0)

        # Sidebar navigation
        self._sidebar = QListWidget()
        self._sidebar.setProperty("sidebar", True)
        self._sidebar.setFixedWidth(200)

        sidebar_items = []
        # Dynamic sidebar based on user permissions
        if self._user.can_manage_products():
            sidebar_items.append("  📦  Products")
        sidebar_items.append("  📊  Transactions")
        if self._user.can_manage_user():
            sidebar_items.append("  👤  Users")

        for item_text in sidebar_items:
            self._sidebar.addItem(item_text)
        self._sidebar.setCurrentRow(0)
        self._sidebar.setSizeAdjustPolicy(
            QListWidget.SizeAdjustPolicy.AdjustToContents
        )
        self._sidebar.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        splitter.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        self._stack.setContentsMargins(0, 0, 0, 0)
        self._stack.addWidget(self._build_products_page())  # index 0
        self._stack.addWidget(self._build_transaction_page())  # index 1
        self._stack.addWidget(self._build_users_page())  # index 2
        splitter.addWidget(self._stack)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

        self._sidebar.currentRowChanged.connect(self._on_sider_changed)

    def _on_sider_changed(self, index: int):
        self._stack.setCurrentIndex(index)
        if index == 0:
            self._refresh_products_table()
        if index == 1:
            self._refresh_transactions()
        if index == 2:
            self._refresh_users_table()

    def _build_top_bar(self) -> QWidget:
        dashboard_btn = (
            "↩ Back to POS",
            self.back_to_main_window.emit
        )

        top_bar = TopBar(
            user=self._user,
            subtitle=f"{STORE_NAME}'s Dashboard",
            actions=[dashboard_btn]
        )
        top_bar.logout_requested.connect(self.logout_requested.emit)
        return top_bar

    # ── Products page ─────────────────────────────────────────────────────────────

    def _build_products_page(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("productsPage")
        widget.setStyleSheet(f"#productsPage {{ background-color: {Colors.BG_PRIMARY}; }}")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(10, 10, 10, 10)
        if self._user.can_manage_products():
            add_btn = QPushButton("+ Add Product")
            add_btn.setFixedHeight(36)
            add_btn.clicked.connect(self._on_add_product)
            toolbar.addWidget(add_btn)
        toolbar.addStretch()

        # Search box
        self._prod_search = QLineEdit()
        self._prod_search.setPlaceholderText("  🔍 Filter products...")
        self._prod_search.setFixedWidth(220)
        self._prod_search.setFixedHeight(36)
        self._prod_search_timer = QTimer(self)
        self._prod_search_timer.setSingleShot(True)
        self._prod_search_timer.setInterval(250)  # Timer to debounce search input, so we don't query on every keystroke
        self._prod_search_timer.timeout.connect(self._refresh_products_table)
        self._prod_search.textChanged.connect(lambda: self._prod_search_timer.start())
        toolbar.addWidget(self._prod_search)
        layout.addLayout(toolbar)

        # Table
        self._prod_table = self._make_product_table()
        self._refresh_products_table()
        layout.addWidget(self._prod_table)

        return widget

    @staticmethod
    def _make_product_table() -> QTableWidget:
        t = QTableWidget()
        t.setProperty("select", "true")

        # Define headers
        header_names = ["ID", "Name", "Price", "Cost", "Stock", "Category", "Actions"]
        t.setColumnCount(len(header_names))
        t.setHorizontalHeaderLabels(header_names)
        t.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # Basic styling
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setSortingEnabled(True)
        t.setMouseTracking(True)
        t.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        t.setShowGrid(False)

        header = t.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Cost
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Stock
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        t.setColumnWidth(6, 250)
        header.setStretchLastSection(False)

        return t

    def _refresh_products_table(self):
        """Directly query the product service with the current search text and update the table."""
        query = self._prod_search.text() if hasattr(self, "_prod_search") else ""
        products = self._product_service.search_product(query)
        self._fill_product_table(self._prod_table, products, show_actions=True)

    def _fill_product_table(self, table: QTableWidget, products, show_actions: bool = False):
        table.setSortingEnabled(False)  # disable while populating to avoid mid-sort issues
        table.setRowCount(0)
        _numeric_cols = {0, 2, 3, 4}

        for p in products:
            r = table.rowCount()
            table.insertRow(r)

            data = [
                str(p.product_id),
                p.name,
                f"HKD${p.price:.1f}",
                f"HKD${p.cost_price:.1f}",
                str(p.stock_quantity),
                CategoryCache.get_name(p.category_id)
            ]

            for col, val in enumerate(data):
                # For number columns, use NumericTableItem to enable proper numeric sorting, but display formatted text
                item = NumericTableItem(val) if col in _numeric_cols else QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

                # Store raw numeric sort key for all numeric columns
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, p.product_id)
                elif col == 2:
                    item.setData(Qt.ItemDataRole.UserRole, p.price)
                elif col == 3:
                    item.setData(Qt.ItemDataRole.UserRole, p.cost_price)
                elif col == 4:
                    item.setData(Qt.ItemDataRole.UserRole, p.stock_quantity)

                # Highlight low stock in red
                if col == 4 and p.stock_quantity <= LOW_STOCK_THRESHOLD:
                    item.setText(f"⚠ {p.stock_quantity} (Low)")
                    item.setForeground(QColor(Colors.DANGER))
                table.setItem(r, col, item)

            if show_actions and self._user.can_manage_products():
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(4, 2, 4, 2)
                action_layout.setSpacing(4)

                edit_btn = QPushButton("Edit")
                edit_btn.setFixedHeight(26)
                edit_btn.setStyleSheet(
                    f"""
                            QPushButton {{
                                background-color: {Colors.ACCENT_LIGHT};
                                color: {Colors.ACCENT};
                                border: none;
                                border-radius: 6px;
                                font-size: 11px;
                                padding: 0 8px;
                                min-height: 0;
                            }}
                            QPushButton:hover {{
                                background-color: {Colors.ACCENT};
                                color: {Colors.TEXT_ON_ACCENT};
                            }}
                     """
                )
                edit_btn.clicked.connect(lambda _, pid=p.product_id: self._on_edit_product(pid))

                del_btn = QPushButton("Delete")
                del_btn.setFixedHeight(26)
                del_btn.setStyleSheet(
                    f"""
                            QPushButton {{
                                background-color: {Colors.DANGER_LIGHT};
                                color: {Colors.DANGER};
                                border: none;
                                border-radius: 6px;
                                font-size: 11px;
                                padding: 0 8px;
                                min-height: 0;
                            }}
                            QPushButton:hover {{
                                background-color: {Colors.DANGER};
                                color: {Colors.TEXT_ON_ACCENT};
                            }}
                        """
                )
                del_btn.clicked.connect(lambda _, pid=p.product_id: self._on_delete_product(pid))

                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                table.setCellWidget(r, 6, action_widget)

        table.setSortingEnabled(True)

    def _on_add_product(self):
        """Open the ProductDialog in "add" mode. If a product is created, save it and refresh the table."""
        dlg = ProductDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            product = dlg.result_product
            if product:
                self._product_service.create_product(
                    product.name,
                    product.price,
                    product.cost_price,
                    product.stock_quantity,
                    product.category_id
                )
                self._refresh_products_table()
                QMessageBox.information(self, "Product Added",
                                        f"#{product.product_id} - {product.name} was added successfully.")

    def _on_edit_product(self, product_id: int):
        """ Open the ProductDialog in "edit" mode with pre-filled data. If updated, save changes and refresh the table."""
        product = self._product_service.get_product_by_id(product_id)
        if not product:
            return
        dlg = ProductDialog(product=product, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.result_product
            if updated:
                self._product_service.update_product(
                    updated.product_id,
                    updated.name,
                    updated.price,
                    updated.cost_price,
                    updated.stock_quantity,
                    updated.category_id
                )
                self._refresh_products_table()
                QMessageBox.information(self, "Product Updated",
                                        f"#{updated.product_id} - {updated.name} was updated successfully.")

    def _on_delete_product(self, product_id: int):
        """Delete the product and refresh the table."""
        product = self._product_service.get_product_by_id(product_id)
        if not product:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"⚠️WARNING : \n #{product.product_id} - {product.name}\n will be permanently deleted from the POS.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._product_service.delete_product(product_id)
            self._refresh_products_table()

    # ── Transactions page ──────────────────────────────────────────────────────────────
    def _build_transaction_page(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("transactionsPage")
        widget.setStyleSheet(f"#transactionsPage {{ background-color: {Colors.BG_PRIMARY}; }}")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(80, 20, 80, 20)
        layout.setSpacing(12)

        hint = QLabel("Double-click a row to view transaction items.")
        hint.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(hint)
        self._transaction_table = self._make_summary_table()
        self._transaction_table.doubleClicked.connect(self._on_transaction_double_clicked)
        layout.addWidget(self._transaction_table)

        return widget

    @staticmethod
    def _make_summary_table() -> QTableWidget:
        t = QTableWidget()
        t.setProperty("select", "true")

        # Define headers
        header_names = ["ID", "Date/Time", "Cashier", "Payment", "Payment Card", "Total", "Status"]

        t.setColumnCount(len(header_names))
        t.setHorizontalHeaderLabels(header_names)
        t.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # Basic styling
        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setSortingEnabled(True)
        t.setMouseTracking(True)
        t.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        t.setShowGrid(False)

        header = t.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Date/Time
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Cashier
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Payment
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status
        t.setColumnWidth(6, 250)
        header.setStretchLastSection(False)
        return t

    def _refresh_transactions(self):
        rows: list[Transaction] = self._transaction_service.get_all_transactions()
        self._transaction_table.setRowCount(0)
        for row in rows:
            r = self._transaction_table.rowCount()
            self._transaction_table.insertRow(r)
            is_void = bool(row.is_void)

            payment = row.payment
            data = [
                str(row.transaction_id),
                row.timestamp,
                self._user_map.get(row.cashier_id).full_name if self._user_map.get(row.cashier_id) else "",
                payment.payment_type.upper(),
                f"**** **** **** {payment.card_number_last4}" if payment.payment_type == PaymentType.CARD else "-",
                f"HKD${payment.total_amount:.1f}",
            ]
            for col, val in enumerate(data):
                if col == 4:
                    item = NumericTableItem(val)
                else:
                    item = QTableWidgetItem(val)

                if is_void:
                    item.setForeground(QColor(Colors.TEXT_MUTED))
                self._transaction_table.setItem(r, col, item)

            status_item = QTableWidgetItem("❌Voided" if is_void else "✅Success")
            if is_void:
                status_item.setForeground(QColor(Colors.DANGER))
            self._transaction_table.setItem(r, 6, status_item)

    def _on_transaction_double_clicked(self, index):
        """Open a dialog showing transaction details and items when a row is double-clicked."""
        id_item = self._transaction_table.item(index.row(), 0)
        if not id_item:
            return
        transaction_id = int(id_item.text())

        transaction = self._transaction_service.get_transaction(transaction_id)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Transaction #{transaction_id} — {transaction.timestamp}")
        dlg.setMinimumSize(600, 360)
        layout = QVBoxLayout(dlg)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        header_row = QHBoxLayout()
        title = QLabel(f"Transaction #{transaction_id}  ·  {transaction.timestamp}")
        title.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {Colors.TEXT};")
        header_row.addWidget(title, stretch=1)
        if transaction.is_void:
            voided_badge = QLabel("❌VOIDED")
            voided_badge.setStyleSheet(
                f"color: {Colors.DANGER}; font-weight: bold; font-size: 12px; "
                f"background: {Colors.DANGER_LIGHT}; border-radius: 6px; padding: 2px 8px;"
            )
            header_row.addWidget(voided_badge)
        layout.addLayout(header_row)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Product", "Unit Price", "Qty", "Line Total"])
        table.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setSortingEnabled(True)
        table.setMouseTracking(True)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setShowGrid(False)

        for row in transaction.items:
            r = table.rowCount()
            table.insertRow(r)
            cells = [
                row.product_name or "—",
                f"HKD${row.unit_price:.1f}",
                str(row.quantity),
                f"HKD${row.line_total:.1f}",
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                align = Qt.AlignmentFlag.AlignLeft
                item.setTextAlignment(align)
                table.setItem(r, col, item)

        layout.addWidget(table)

        total_lbl = QLabel(f"Total: HKD${transaction.payment.total_amount}")
        total_lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {Colors.ACCENT};"
        )
        total_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(total_lbl)

        btn_row = QHBoxLayout()

        #  Only show "Void" button if user has permission and transaction is not already voided
        if self._user.can_manage_products() and not transaction.is_void:
            void_btn = QPushButton("Void Transaction")
            void_btn.setFixedHeight(32)
            void_btn.setProperty("danger", "true")

            def _do_void():
                msg = QMessageBox(dlg)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Confirm Void")
                msg.setText(f"Void Transaction #{transaction_id}?\n\nThis cannot be undone.")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                msg.setDefaultButton(QMessageBox.StandardButton.No)

                reply = msg.exec()
                if reply == QMessageBox.StandardButton.Yes:
                    self._transaction_service.void_transaction(transaction_id)
                    self._refresh_transactions()
                    dlg.accept()

            void_btn.clicked.connect(_do_void)
            btn_row.addWidget(void_btn)

        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        dlg.exec()

    # ── Users page ────────────────────────────────────────────────────────────────

    def _build_users_page(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("usersPage")
        widget.setStyleSheet(f"#usersPage {{ background-color: {Colors.BG_PRIMARY}; }}")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self._users_table = self._make_users_table()

        # horizontal center
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self._users_table)
        row.addStretch()
        layout.addLayout(row)

        layout.addStretch()

        return widget

    @staticmethod
    def _make_users_table() -> QTableWidget:
        t = QTableWidget()
        t.setProperty("select", "true")

        header_names = ["ID", "Username", "Full Name", "Role"]
        t.setColumnCount(len(header_names))
        t.setHorizontalHeaderLabels(header_names)
        t.horizontalHeader().setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        t.setAlternatingRowColors(True)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setSortingEnabled(True)
        t.setMouseTracking(True)
        t.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        t.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        t.setShowGrid(False)

        header = t.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Username
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Full Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Role
        header.setStretchLastSection(False)

        t.setFixedSize(650, 700)

        return t

    def _refresh_users_table(self):
        rows = self._user_service.get_all_user()
        self._users_table.setRowCount(0)
        for row in rows:
            r = self._users_table.rowCount()
            self._users_table.insertRow(r)
            data = [
                str(row.user_id),
                row.username,
                row.full_name,
                row.role.capitalize()
            ]
            for col, val in enumerate(data):
                item = QTableWidgetItem(val)

                if row.role == UserRole.MANAGER:
                    item.setForeground(QColor(Colors.ACCENT))
                self._users_table.setItem(r, col, item)
