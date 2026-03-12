import sys

from PySide6.QtWidgets import QApplication

from database.db_manager import DatabaseManager
from database.seed_data import run_seed
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from gui.styles import StyleEngine
from models.user import User


class App:
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setApplicationName("Smart POS")

        # Apply global stylesheet
        StyleEngine.apply(self._app)

        # Database setup and seeding
        self._db = DatabaseManager.get_instance()
        run_seed()

        self._current_user: User | None = None
        self._login_window: LoginWindow | None = None
        self._main_window: MainWindow | None = None

    def _show_login(self):
        if self._main_window:
            self._main_window.hide()

        if self._login_window is None:
            self._login_window = LoginWindow(self._db)
            self._login_window.login_success.connect(self._on_login_success)
        self._login_window.show()

    def _on_login_success(self, user: User):
        self._current_user = user
        if self._login_window:
            self._login_window.hide()

        if self._current_user:
            self._show_main_window()

    def _show_main_window(self):
        if self._main_window is None:
            self._main_window = MainWindow(self._current_user, self._db)
            self._main_window.logout_requested.connect(self._on_logout)
        self._main_window.show()

    def _on_logout(self):
        self._current_user = None
        if self._main_window:
            self._main_window.close()
            self._main_window = None
        self._show_login()

    def run(self) -> int:
        self._show_login()
        return self._app.exec()


if __name__ == '__main__':
    app = App()
    sys.exit(app.run())
