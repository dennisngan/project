from datetime import datetime

from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton

from constant.constants import ROLE_EMOJI
from database.db_manager import DatabaseManager
from gui.styles import Colors
from models.user import User


class MainWindow(QMainWindow):
    open_manager_panel = Signal()
    logout_requested = Signal()

    def __init__(self, user: User, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self._user = user
        self._db = db
        self._setup_ui()
        self._start_clock()

    def _setup_ui(self):
        self.setWindowTitle("Quck Store - POS System")
        self.setFixedSize(1100, 680)

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
        content.addWidget(self._build_product_panel(), stretch=6)
        content.addWidget(self._build_cart_panel(), stretch=4)
        root.addLayout(content)

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

    # Clock
    def _start_clock(self):
        self._update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1_000)  # Update every second

    def _update_clock(self):
        now = datetime.now().strftime("%b %d, %Y  %H:%M:%S")
        self._clock_lbl.setText(f"🕐 {now}")

    def _build_product_panel(self) -> QWidget:
        return QWidget()

    def _build_cart_panel(self) -> QWidget:
        return QWidget()
