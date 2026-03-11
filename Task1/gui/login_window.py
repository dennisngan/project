from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QSizePolicy

from database.db_manager import DatabaseManager
from gui.styles import Colors, StyleEngine
from services.auth_service import AuthService


class LoginWindow(QWidget):
    # Signal emitted when login is successful, passing the authenticated User object
    login_success = Signal(object)

    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self._db = db
        self._auth_service = AuthService(db)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Smart POS — Login")
        self.setFixedSize(500, 640)

        # Outer layout
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(0, 0, 0, 0)

        # Cart frame
        card = QFrame()
        card.setProperty("card", True)
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(48, 48, 48, 48)

        # App icon placeholder — blue rounded square, Apple-style
        icon_frame = QFrame()
        icon_frame.setFixedSize(52, 52)
        icon_frame.setStyleSheet(
            f"background-color: {Colors.BG_PRIMARY}; border-radius: 10px; border: none;"
        )
        icon_inner = QVBoxLayout(icon_frame)
        icon_inner.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel("🏪")
        icon_lbl.setStyleSheet(
            f"color: {Colors.TEXT_ON_ACCENT}; font-size: 50px; font-weight: bold; "
            f"background: transparent;"
        )
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_inner.addWidget(icon_lbl)
        card_layout.addWidget(icon_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo = QLabel(StyleEngine.make_logo_label_text())
        logo.setStyleSheet(StyleEngine.logo_stylesheet())
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo)

        # Subtitle
        subtitle = QLabel("Powered by Smart POS")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 14px;")
        card_layout.addWidget(subtitle)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {Colors.BORDER};")
        card_layout.addWidget(divider)

        # Username
        user_label = QLabel("Username")
        user_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;"
        )
        card_layout.addWidget(user_label)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Enter your username")
        self._username_input.setMinimumHeight(34)
        card_layout.addWidget(self._username_input)

        # Password
        pass_label = QLabel("Password")
        pass_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;"
        )
        card_layout.addWidget(pass_label)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Enter your password")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setMinimumHeight(34)
        self._password_input.returnPressed.connect(self._on_login)
        card_layout.addWidget(self._password_input)

        # Sign In button
        self._login_btn = QPushButton("Sign In")
        self._login_btn.setMinimumHeight(46)
        self._login_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(self._login_btn)

        # Error label (hidden by default)
        self._error_label = QLabel("")
        self._error_label.setFixedHeight(12)
        self._error_label.setStyleSheet(f"color: {Colors.DANGER}; font-size: 12px;")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        size_policy = self._error_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self._error_label.setSizePolicy(size_policy)

        self._error_label.hide()
        card_layout.addWidget(self._error_label)

        # Version footer
        version_label = QLabel("v1.0.0 · © 2026 Quick Store")
        version_label.setStyleSheet(f"color: {Colors.BORDER_STRONG}; font-size: 11px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(version_label)

        outer.addWidget(card)

    def _on_login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

        user = self._auth_service.authenticate(username, password)

        if user is None:
            self._show_error("Invalid username or password. Please try again.")
            self._password_input.clear()
            return

        if user:
            self._error_label.hide()
            self._username_input.clear()
            self._password_input.clear()
            self.login_success.emit(user)

    def _show_error(self, message: str):
        self._error_label.setText(f'❌ {message}')
        self._error_label.show()
        self._password_input.clear()
        self._password_input.setFocus()
