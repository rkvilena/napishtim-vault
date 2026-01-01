"""Clipboard management with auto-clear functionality."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QObject, pyqtSignal

# Auto-clear clipboard after this many milliseconds
CLIPBOARD_CLEAR_MS = 30_000  # 30 seconds


class ClipboardManager(QObject):
    """Manages clipboard operations with automatic clearing."""

    cleared = pyqtSignal()  # Emitted when clipboard is cleared

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._clear_clipboard)
        self._last_copied: str = ""

    def copy(self, text: str) -> None:
        """
        Copy text to clipboard and start auto-clear timer.

        Args:
            text: The text to copy
        """
        clipboard = QApplication.clipboard()
        if clipboard:
            self._last_copied = text
            clipboard.setText(text)

            # Restart timer
            self._timer.stop()
            self._timer.start(CLIPBOARD_CLEAR_MS)

    def _clear_clipboard(self) -> None:
        """Clear the clipboard if it still contains our copied text."""
        clipboard = QApplication.clipboard()
        if clipboard:
            current = clipboard.text()
            # Only clear if clipboard still has what we copied
            if current == self._last_copied:
                clipboard.clear()
                # Also try to overwrite with empty string
                clipboard.setText("")

        self._last_copied = ""
        self.cleared.emit()

    def force_clear(self) -> None:
        """Immediately clear the clipboard."""
        self._timer.stop()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.clear()
            clipboard.setText("")
        self._last_copied = ""
        self.cleared.emit()

    def cancel_timer(self) -> None:
        """Cancel the auto-clear timer without clearing."""
        self._timer.stop()
