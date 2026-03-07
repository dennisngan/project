class WeakPasswordException(Exception):
    """Raised when a user attempts to set a password that doesn't meet security criteria."""
    pass


class UsernameTakenException(Exception):
    """Raised when a user attempts to register with a username that already exists."""
    pass
