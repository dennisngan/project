from PySide6.QtWidgets import QLineEdit


class HKDLineEdit(QLineEdit):
    """
    Custom QLineEdit that enforces a non-deletable 'HKD$ ' prefix.

    Inherits from QLineEdit (Inheritance / Polymorphism — overrides Qt's text-change
    and cursor-position signals via slots).  The prefix is stored as a class-level
    private constant (_PREFIX) and exposed read-only through a @property accessor
    (Encapsulation).
    """

    _PREFIX = "HKD$ "

    def __init__(self, parent=None):
        super().__init__(parent)
        self.blockSignals(True)
        self.setText(self._PREFIX)
        self.blockSignals(False)
        self.textChanged.connect(self._enforce_prefix)
        self.cursorPositionChanged.connect(self._clamp_cursor)

    def _enforce_prefix(self, text: str):
        if text.startswith(self._PREFIX):
            return
        self.blockSignals(True)
        # Preserve whatever numeric part remains after prefix length
        numeric = text[len(self._PREFIX):] if len(text) >= len(self._PREFIX) else ""
        restored = self._PREFIX + numeric
        self.setText(restored)
        self.setCursorPosition(len(restored))
        self.blockSignals(False)

    def _clamp_cursor(self, _old: int, new: int):
        if new < len(self._PREFIX):
            self.setCursorPosition(len(self._PREFIX))

    def numeric_value(self) -> float:
        """Strip the prefix and return the numeric portion as a float (0.0 on invalid input)."""
        try:
            return float(self.text()[len(self._PREFIX):])
        except ValueError:
            return 0.0

    @property
    def PREFIX(self):
        return self._PREFIX
