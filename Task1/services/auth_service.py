from database.db_manager import DatabaseManager
from models.user import User
from utils import password_utils


class AuthService:
    def __init__(self, db: DatabaseManager):
        self._db = db

    def authenticate(self, username: str, password: str) -> User | None:
        """
        Validate credentials and return a User object on success, or None on failure.
        """
        sql = "SELECT * FROM users WHERE username = ?"
        row = self._db.fetchone(sql, (username,))
        if row is None:
            return None

        """
        Check the provided password against the stored hash
        Never store password or password hash in the User object after authentication.
        """
        if password_utils.check_password(password, row["password_hash"]):
            return User.from_db_row(row)

        return None
