"""Dark theme stylesheet for NapishtimVault."""

# Color palette
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "text": "#eaeaea",
    "text_dim": "#a0a0a0",
    "border": "#2a2a4a",
    "success": "#4ecca3",
    "warning": "#ffc107",
    "error": "#e94560",
    "input_bg": "#0d1b2a",
}

DARK_STYLESHEET = f"""
/* Main Window */
QMainWindow, QWidget {{
    background-color: {COLORS["bg_dark"]};
    color: {COLORS["text"]};
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}}

/* Frames and Containers */
QFrame {{
    background-color: {COLORS["bg_medium"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

QFrame#headerFrame {{
    background-color: transparent;
    border: none;
}}

/* Labels */
QLabel {{
    color: {COLORS["text"]};
    background-color: transparent;
    border: none;
}}

QLabel#titleLabel {{
    font-size: 24px;
    font-weight: bold;
    color: {COLORS["accent"]};
}}

QLabel#subtitleLabel {{
    font-size: 14px;
    color: {COLORS["text_dim"]};
}}

QLabel#errorLabel {{
    color: {COLORS["error"]};
    font-size: 12px;
}}

QLabel#successLabel {{
    color: {COLORS["success"]};
    font-size: 12px;
}}

/* Line Edits / Input Fields */
QLineEdit {{
    background-color: {COLORS["input_bg"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 13px;
    selection-background-color: {COLORS["accent"]};
}}

QLineEdit:focus {{
    border: 1px solid {COLORS["accent"]};
}}

QLineEdit:disabled {{
    background-color: {COLORS["bg_medium"]};
    color: {COLORS["text_dim"]};
}}

/* Text Edit */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS["input_bg"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    selection-background-color: {COLORS["accent"]};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {COLORS["accent"]};
}}

/* Push Buttons */
QPushButton {{
    background-color: {COLORS["bg_light"]};
    color: {COLORS["text"]};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS["accent"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["accent_hover"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["border"]};
    color: {COLORS["text_dim"]};
}}

QPushButton#primaryButton {{
    background-color: {COLORS["accent"]};
    color: white;
    font-weight: bold;
}}

QPushButton#primaryButton:hover {{
    background-color: {COLORS["accent_hover"]};
}}

QPushButton#dangerButton {{
    background-color: transparent;
    color: {COLORS["error"]};
    border: 1px solid {COLORS["error"]};
}}

QPushButton#dangerButton:hover {{
    background-color: {COLORS["error"]};
    color: white;
}}

QPushButton#iconButton {{
    background-color: transparent;
    border: none;
    padding: 6px;
    min-width: 32px;
    max-width: 32px;
    border-radius: 4px;
}}

QPushButton#iconButton:hover {{
    background-color: {COLORS["bg_light"]};
}}

/* List Widget */
QListWidget {{
    background-color: {COLORS["bg_medium"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}

QListWidget::item {{
    background-color: transparent;
    color: {COLORS["text"]};
    border-radius: 6px;
    padding: 12px;
    margin: 2px 4px;
}}

QListWidget::item:hover {{
    background-color: {COLORS["bg_light"]};
}}

QListWidget::item:selected {{
    background-color: {COLORS["accent"]};
    color: white;
}}

/* Scroll Bars */
QScrollBar:vertical {{
    background-color: {COLORS["bg_dark"]};
    width: 10px;
    border-radius: 5px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["bg_light"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["bg_dark"]};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS["border"]};
    border-radius: 5px;
    min-width: 30px;
}}

/* Dialog */
QDialog {{
    background-color: {COLORS["bg_dark"]};
}}

/* Message Box */
QMessageBox {{
    background-color: {COLORS["bg_dark"]};
}}

QMessageBox QLabel {{
    color: {COLORS["text"]};
}}

/* Menu */
QMenu {{
    background-color: {COLORS["bg_medium"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS["accent"]};
}}

/* Tool Tips */
QToolTip {{
    background-color: {COLORS["bg_medium"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    padding: 6px;
}}

/* Status Bar */
QStatusBar {{
    background-color: {COLORS["bg_medium"]};
    color: {COLORS["text_dim"]};
    border-top: 1px solid {COLORS["border"]};
}}

/* Group Box */
QGroupBox {{
    background-color: transparent;
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
}}

QGroupBox::title {{
    color: {COLORS["text_dim"]};
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}}
"""
