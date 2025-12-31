"""Idle detection and auto-lock functionality."""

from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QEvent
from PyQt6.QtWidgets import QApplication

# Auto-lock after this many milliseconds of inactivity
IDLE_TIMEOUT_MS = 3 * 60 * 1000  # 3 minutes


class IdleMonitor(QObject):
    """Monitors user activity and triggers auto-lock."""
    
    idle_timeout = pyqtSignal()  # Emitted when idle timeout reached
    minimized = pyqtSignal()    # Emitted when window is minimized
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)
        self._enabled = False
        self._main_window = None
    
    def start(self, window=None) -> None:
        """
        Start monitoring for idle.
        
        Args:
            window: The main window to monitor for minimize events
        """
        self._enabled = True
        self._main_window = window
        
        # Install event filter on application to catch all events
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
        
        self._reset_timer()
    
    def stop(self) -> None:
        """Stop monitoring."""
        self._enabled = False
        self._timer.stop()
        
        app = QApplication.instance()
        if app:
            app.removeEventFilter(self)
    
    def _reset_timer(self) -> None:
        """Reset the idle timer."""
        if self._enabled:
            self._timer.stop()
            self._timer.start(IDLE_TIMEOUT_MS)
    
    def _on_timeout(self) -> None:
        """Handle idle timeout."""
        if self._enabled:
            self.idle_timeout.emit()
    
    def eventFilter(self, obj, event: QEvent) -> bool:
        """Filter events to detect user activity."""
        if self._enabled:
            event_type = event.type()
            
            # Reset timer on user interaction events
            if event_type in (
                QEvent.Type.MouseMove,
                QEvent.Type.MouseButtonPress,
                QEvent.Type.MouseButtonRelease,
                QEvent.Type.KeyPress,
                QEvent.Type.KeyRelease,
                QEvent.Type.Wheel,
            ):
                self._reset_timer()
            
            # Detect window minimize
            elif event_type == QEvent.Type.WindowStateChange:
                if self._main_window and obj == self._main_window:
                    from PyQt6.QtCore import Qt
                    if self._main_window.windowState() & Qt.WindowState.WindowMinimized:
                        self.minimized.emit()
        
        # Don't filter the event, let it propagate
        return False
    
    def pause(self) -> None:
        """Temporarily pause the idle timer."""
        self._timer.stop()
    
    def resume(self) -> None:
        """Resume the idle timer."""
        if self._enabled:
            self._reset_timer()
