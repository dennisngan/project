"""
Entry point for the SmartPOS application.
Manages the application lifecycle: initialises the database, seeds default data,
and orchestrates window transitions (Login → Main POS → Dashboard) using Qt signals.
"""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from database.db_manager import DatabaseManager
from database.seed_data import run_seed
from gui.dashborad_window import DashboardWindow
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.styles import StyleEngine
from models.user import User
from utils.path_utils import get_resource_base_dir


class App:
    """
    Root application controller.
    """

    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setApplicationName("Smart POS")
        icon_path = get_resource_base_dir() / "asset" / "store_icon.ico"
        self._app.setWindowIcon(QIcon(str(icon_path)))

        # Apply global stylesheet
        StyleEngine.apply(self._app)

        # Database setup and seeding
        self._db = DatabaseManager.get_instance()
        run_seed()

        self._current_user: User | None = None
        self._login_window: LoginWindow | None = None
        self._main_window: MainWindow | None = None
        self._dashboard_window: DashboardWindow | None = None

    def _show_login(self):
        if self._login_window is None:
            self._login_window = LoginWindow(self._db)
            self._login_window.login_success.connect(self._on_login_success)
        self._login_window.show()

    def _on_login_success(self, user: User):
        self._current_user = user
        if self._login_window:
            self._login_window.hide()

        if self._current_user:
            self._on_show_main_window()

    def _on_show_main_window(self):
        if self._current_user and self._main_window is None:
            self._main_window = MainWindow(self._current_user, self._db)
            self._main_window.logout_requested.connect(self._on_logout)
            self._main_window.open_dashboard.connect(self._on_show_dashboard)
        if self._dashboard_window:
            self._dashboard_window.hide()
            self._dashboard_window = None  # Force dashboard window to be recreated on next open
        self._main_window.show()
        self._main_window.invalidate_cache()

    def _on_show_dashboard(self):
        if self._current_user and self._dashboard_window is None:
            self._dashboard_window = DashboardWindow(self._current_user, self._db)
            self._dashboard_window.back_to_main_window.connect(self._on_show_main_window)
            self._dashboard_window.logout_requested.connect(self._on_logout)
        if self._main_window:
            self._main_window.hide()
        self._dashboard_window.show()

    def _on_logout(self):
        self._current_user = None

        for attr in ("_login_window", "_main_window", "_dashboard_window"):
            self._close_window(attr)

        self._show_login()

    def _close_window(self, attr_name: str):
        """Safely close and destroy a window, then clear its reference via setattr."""
        window = getattr(self, attr_name, None)
        if window is not None:
            window.close()
            window.deleteLater()
            setattr(self, attr_name, None)

    def run(self) -> int:
        self._show_login()
        return self._app.exec()


if __name__ == '__main__':
    app = App()
    sys.exit(app.run())
