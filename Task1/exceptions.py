"""
Domain-specific custom exceptions.

Both exceptions inherit from Python's built-in Exception class (Inheritance),
allowing callers to catch them with a specific except clause and keep error-handling
logic distinct from generic runtime errors.
"""


class WeakPasswordException(Exception):
    """Raised when a user attempts to set a password that doesn't meet security criteria."""
    pass


class UsernameTakenException(Exception):
    """Raised when a user attempts to register with a username that already exists."""
    pass
