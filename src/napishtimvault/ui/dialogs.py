"""Dialog windows for adding/editing credentials."""

import secrets
import string
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QFrame,
    QMessageBox, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..models import Credential


class CredentialDialog(QDialog):
    """Dialog for adding or editing a credential."""
    
    def __init__(self, credential: Optional[Credential] = None, parent=None):
        super().__init__(parent)
        self.credential = credential
        self.result_credential: Optional[Credential] = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Edit Credential" if self.credential else "Add Credential")
        self.setMinimumWidth(420)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel("Title *")
        layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Gmail, GitHub, Netflix")
        if self.credential:
            self.title_input.setText(self.credential.title)
        layout.addWidget(self.title_input)
        
        # Username
        username_label = QLabel("Username *")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., john@example.com")
        if self.credential:
            self.username_input.setText(self.credential.username)
        layout.addWidget(self.username_input)
        
        # Password
        pwd_label = QLabel("Password *")
        layout.addWidget(pwd_label)
        
        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        if self.credential:
            self.password_input.setText(self.credential.password)
        pwd_row.addWidget(self.password_input, 1)
        
        # Toggle visibility button
        self.show_pwd_btn = QPushButton("👁")
        self.show_pwd_btn.setObjectName("iconButton")
        self.show_pwd_btn.setToolTip("Show/Hide password")
        self.show_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_pwd_btn.clicked.connect(self._toggle_password_visibility)
        pwd_row.addWidget(self.show_pwd_btn)
        
        # Generate button
        gen_btn = QPushButton("🎲")
        gen_btn.setObjectName("iconButton")
        gen_btn.setToolTip("Generate password")
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.clicked.connect(self._show_generator)
        pwd_row.addWidget(gen_btn)
        
        layout.addLayout(pwd_row)
        
        # Password generator options (hidden by default)
        self.generator_frame = QFrame()
        self.generator_frame.setStyleSheet("""
            QFrame {
                background-color: #0d1b2a;
                border: 1px solid #2a2a4a;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        gen_layout = QVBoxLayout(self.generator_frame)
        gen_layout.setSpacing(8)
        
        gen_header = QLabel("Password Generator")
        gen_header.setStyleSheet("font-weight: bold; color: #e94560;")
        gen_layout.addWidget(gen_header)
        
        # Length
        len_row = QHBoxLayout()
        len_row.addWidget(QLabel("Length:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        len_row.addWidget(self.length_spin)
        len_row.addStretch()
        gen_layout.addLayout(len_row)
        
        # Options
        self.uppercase_check = QCheckBox("Uppercase (A-Z)")
        self.uppercase_check.setChecked(True)
        gen_layout.addWidget(self.uppercase_check)
        
        self.lowercase_check = QCheckBox("Lowercase (a-z)")
        self.lowercase_check.setChecked(True)
        gen_layout.addWidget(self.lowercase_check)
        
        self.digits_check = QCheckBox("Digits (0-9)")
        self.digits_check.setChecked(True)
        gen_layout.addWidget(self.digits_check)
        
        self.symbols_check = QCheckBox("Symbols (!@#$...)")
        self.symbols_check.setChecked(True)
        gen_layout.addWidget(self.symbols_check)
        
        # Generate button in frame
        gen_now_btn = QPushButton("Generate")
        gen_now_btn.setObjectName("primaryButton")
        gen_now_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_now_btn.clicked.connect(self._generate_password)
        gen_layout.addWidget(gen_now_btn)
        
        layout.addWidget(self.generator_frame)
        self.generator_frame.hide()
        
        # URL
        url_label = QLabel("URL")
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        if self.credential and self.credential.url:
            self.url_input.setText(self.credential.url)
        layout.addWidget(self.url_input)
        
        # Notes
        notes_label = QLabel("Notes")
        layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes...")
        self.notes_input.setMaximumHeight(80)
        if self.credential and self.credential.notes:
            self.notes_input.setPlainText(self.credential.notes)
        layout.addWidget(self.notes_input)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        layout.addSpacing(8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Focus title
        self.title_input.setFocus()
    
    def _toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pwd_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pwd_btn.setText("👁")
    
    def _show_generator(self):
        self.generator_frame.setVisible(not self.generator_frame.isVisible())
        # Ensure the dialog resizes back when the generator is hidden.
        self.adjustSize()
        self.resize(self.sizeHint())
    
    def _generate_password(self):
        chars = ""
        if self.uppercase_check.isChecked():
            chars += string.ascii_uppercase
        if self.lowercase_check.isChecked():
            chars += string.ascii_lowercase
        if self.digits_check.isChecked():
            chars += string.digits
        if self.symbols_check.isChecked():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        length = self.length_spin.value()
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        self.password_input.setText(password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        self.show_pwd_btn.setText("🙈")
    
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
    
    def _on_save(self):
        title = self.title_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        url = self.url_input.text().strip() or None
        notes = self.notes_input.toPlainText().strip() or None
        
        # Validation
        if not title:
            self._show_error("Title is required")
            self.title_input.setFocus()
            return
        
        if not username:
            self._show_error("Username is required")
            self.username_input.setFocus()
            return
        
        if not password:
            self._show_error("Password is required")
            self.password_input.setFocus()
            return
        
        self.result_credential = Credential(
            id=self.credential.id if self.credential else None,
            title=title,
            username=username,
            password=password,
            url=url,
            notes=notes,
        )
        
        self.accept()


class ConfirmDialog(QMessageBox):
    """Confirmation dialog with dark theme."""
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Question)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.setDefaultButton(QMessageBox.StandardButton.No)
    
    @staticmethod
    def confirm(title: str, message: str, parent=None) -> bool:
        """Show confirmation dialog and return True if confirmed."""
        dialog = ConfirmDialog(title, message, parent)
        return dialog.exec() == QMessageBox.StandardButton.Yes


class ChangeMasterPasswordDialog(QDialog):
    """Dialog for changing the master password."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_password: str = ""
        self.new_password: str = ""
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Change Master Password")
        self.setMinimumWidth(420)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Change Master Password")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        info = QLabel("This will re-encrypt all saved passwords with the new master password.")
        info.setObjectName("subtitleLabel")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addSpacing(6)

        layout.addWidget(QLabel("Current Password"))
        current_row = QHBoxLayout()
        current_row.setSpacing(8)

        self.current_input = QLineEdit()
        self.current_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_input.setPlaceholderText("Enter current master password")
        current_row.addWidget(self.current_input, 1)

        self.show_current_btn = QPushButton("👁")
        self.show_current_btn.setObjectName("iconButton")
        self.show_current_btn.setToolTip("Show/Hide password")
        self.show_current_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_current_btn.clicked.connect(self._toggle_current_visibility)
        current_row.addWidget(self.show_current_btn)

        layout.addLayout(current_row)

        layout.addWidget(QLabel("New Password"))
        new_row = QHBoxLayout()
        new_row.setSpacing(8)

        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_input.setPlaceholderText("Enter new master password")
        new_row.addWidget(self.new_input, 1)

        self.show_new_btn = QPushButton("👁")
        self.show_new_btn.setObjectName("iconButton")
        self.show_new_btn.setToolTip("Show/Hide password")
        self.show_new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_new_btn.clicked.connect(self._toggle_new_visibility)
        new_row.addWidget(self.show_new_btn)

        layout.addLayout(new_row)

        layout.addWidget(QLabel("Confirm New Password"))
        confirm_row = QHBoxLayout()
        confirm_row.setSpacing(8)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm new master password")
        self.confirm_input.returnPressed.connect(self._on_submit)
        confirm_row.addWidget(self.confirm_input, 1)

        self.show_confirm_btn = QPushButton("👁")
        self.show_confirm_btn.setObjectName("iconButton")
        self.show_confirm_btn.setToolTip("Show/Hide password")
        self.show_confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_confirm_btn.clicked.connect(self._toggle_confirm_visibility)
        confirm_row.addWidget(self.show_confirm_btn)

        layout.addLayout(confirm_row)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()

        submit_btn = QPushButton("Change Password")
        submit_btn.setObjectName("primaryButton")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(submit_btn)

        layout.addLayout(btn_row)

        self.current_input.setFocus()

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()

    def _hide_error(self):
        self.error_label.hide()

    def _toggle_current_visibility(self):
        if self.current_input.echoMode() == QLineEdit.EchoMode.Password:
            self.current_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_current_btn.setText("🙈")
        else:
            self.current_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_current_btn.setText("👁")

    def _toggle_new_visibility(self):
        if self.new_input.echoMode() == QLineEdit.EchoMode.Password:
            self.new_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_new_btn.setText("🙈")
        else:
            self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_new_btn.setText("👁")

    def _toggle_confirm_visibility(self):
        if self.confirm_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_confirm_btn.setText("🙈")
        else:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_confirm_btn.setText("👁")

    def _on_submit(self):
        self._hide_error()

        current_pwd = self.current_input.text()
        new_pwd = self.new_input.text()
        confirm = self.confirm_input.text()

        if not current_pwd:
            self._show_error("Current password is required")
            return

        if not new_pwd:
            self._show_error("New password is required")
            return

        if len(new_pwd) < 8:
            self._show_error("New password must be at least 8 characters")
            return

        if new_pwd != confirm:
            self._show_error("New passwords do not match")
            return

        self.current_password = current_pwd
        self.new_password = new_pwd

        # Best-effort: clear inputs before closing
        self.current_input.clear()
        self.new_input.clear()
        self.confirm_input.clear()

        # Reset visibility
        self.current_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_current_btn.setText("👁")
        self.show_new_btn.setText("👁")
        self.show_confirm_btn.setText("👁")

        self.accept()
