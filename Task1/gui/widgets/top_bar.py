from datetime import datetime
from typing import Callable, Optional

from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget, QVBoxLayout, QPushButton

from config import STORE_NAME
from constant.constants import ROLE_EMOJI
from gui.styles import Colors
from models.user import User


class TopBar(QFrame):
    """
    Top navigation bar for the POS interface.
    """
    logout_requested = Signal()

    def __init__(self,
                 user: User,
                 parent=None,
                 actions: Optional[list[tuple[str, Callable]]] = None,
                 title: Optional[str] = None,
                 subtitle: str = "POS System",
                 status_color: str = Colors.STATUS_ONLINE):
        super().__init__(parent)
        self._user = user
        self._actions = actions or []

        # dynamic branding configuration
        self._title = title if title is not None else f"🏪 {STORE_NAME}"
        self._subtitle = subtitle
        self._status_color = status_color

        self._setup_ui()
        self._start_clock()

    def _setup_ui(self):
        self.setStyleSheet(
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
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # Dynamic Branding
        dot = QLabel()
        dot.setFixedSize(10, 10)
        # Use the dynamic status color
        dot.setStyleSheet(
            f"background-color: {self._status_color}; border-radius: 5px; "
            f"min-width: 10px; min-height: 10px; border: none;"
        )
        layout.addWidget(dot)

        # Use the dynamic title
        logo = QLabel(self._title)
        logo.setObjectName("logo")
        layout.addWidget(logo)

        sep = QLabel("|")
        sep.setObjectName("separator")
        layout.addWidget(sep)

        # Use the dynamic subtitle
        pos_lbl = QLabel(self._subtitle)
        pos_lbl.setObjectName("pos_label")
        layout.addWidget(pos_lbl)

        layout.addStretch()

        # User Info Bubble
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

        # Dynamic Actions
        for text, callback in self._actions:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, cb=callback: cb())
            layout.addWidget(btn)

        # Logout Button
        logout_btn = QPushButton("⏻ Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setProperty("danger", "true")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

    def _start_clock(self):
        """Start a timer to update the clock every second."""
        self._update_clock()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_clock)
        self._timer.start(1_000)

    def _update_clock(self):
        now = datetime.now().strftime("%b %d, %Y  %H:%M:%S")
        self._clock_lbl.setText(f"🕐 {now}")
