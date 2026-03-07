from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Enforces and to_dict() contract on subclasses."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize the object to a plain dictionary."""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"
