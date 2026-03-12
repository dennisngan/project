from PySide6.QtWidgets import QLineEdit


class HKDLineEdit(QLineEdit):
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
        try:
            return float(self.text()[len(self._PREFIX):])
        except ValueError:
            return 0.0

    @property
    def PREFIX(self):
        return self._PREFIX
