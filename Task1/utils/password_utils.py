import bcrypt

from config import SALT_ROUNDS


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    Args:
        password: The plain-text password to hash.

    Returns:
        A securely hashed password as a string.
    """
    salt = bcrypt.gensalt(rounds=SALT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored hash.

    Args:
        password: The plain-text password to check.
        hashed_password: The stored hash to compare against.

    Returns:
        True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
