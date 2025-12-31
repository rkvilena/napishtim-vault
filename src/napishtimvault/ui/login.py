"""Login and setup screens."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class SetupWidget(QWidget):
    """First-time setup screen for creating master password."""
    
    setup_complete = pyqtSignal(str)  # Emits the master password
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Spacer at top
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Center container
        container = QFrame()
        container.setObjectName("headerFrame")
        container.setMaximumWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        
        # Logo/Title
        title = QLabel("🔐 NapishtimVault")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Create your master password")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(subtitle)
        
        container_layout.addSpacing(20)
        
        # Password field
        pwd_label = QLabel("Master Password")
        container_layout.addWidget(pwd_label)
        
        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter a strong password")
        pwd_row.addWidget(self.password_input, 1)

        self.show_pwd_btn = QPushButton("👁")
        self.show_pwd_btn.setObjectName("iconButton")
        self.show_pwd_btn.setToolTip("Show/Hide password")
        self.show_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_pwd_btn.clicked.connect(self._toggle_password_visibility)
        pwd_row.addWidget(self.show_pwd_btn)

        container_layout.addLayout(pwd_row)
        
        # Confirm password field
        confirm_label = QLabel("Confirm Password")
        container_layout.addWidget(confirm_label)
        
        confirm_row = QHBoxLayout()
        confirm_row.setSpacing(8)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.returnPressed.connect(self._on_submit)
        confirm_row.addWidget(self.confirm_input, 1)

        self.show_confirm_btn = QPushButton("👁")
        self.show_confirm_btn.setObjectName("iconButton")
        self.show_confirm_btn.setToolTip("Show/Hide password")
        self.show_confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_confirm_btn.clicked.connect(self._toggle_confirm_visibility)
        confirm_row.addWidget(self.show_confirm_btn)

        container_layout.addLayout(confirm_row)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        container_layout.addWidget(self.error_label)
        
        container_layout.addSpacing(10)
        
        # Submit button
        self.submit_btn = QPushButton("Create Vault")
        self.submit_btn.setObjectName("primaryButton")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._on_submit)
        container_layout.addWidget(self.submit_btn)
        
        # Info text
        info = QLabel("Remember this password! It cannot be recovered.")
        info.setObjectName("subtitleLabel")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        container_layout.addWidget(info)
        
        # Center the container
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(container)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        
        # Spacer at bottom
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Focus password field
        self.password_input.setFocus()
    
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
    
    def _hide_error(self):
        self.error_label.hide()

    def _toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pwd_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pwd_btn.setText("👁")

    def _toggle_confirm_visibility(self):
        if self.confirm_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_confirm_btn.setText("🙈")
        else:
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_confirm_btn.setText("👁")
    
    def _on_submit(self):
        self._hide_error()
        
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Validation
        if not password:
            self._show_error("Password is required")
            return
        
        if len(password) < 8:
            self._show_error("Password must be at least 8 characters")
            return
        
        if password != confirm:
            self._show_error("Passwords do not match")
            return
        
        self.setup_complete.emit(password)
        
        # Clear inputs for security
        self.password_input.clear()
        self.confirm_input.clear()

        # Reset visibility
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_pwd_btn.setText("👁")
        self.show_confirm_btn.setText("👁")


class LoginWidget(QWidget):
    """Login screen for unlocking the vault."""
    
    login_success = pyqtSignal(str)  # Emits the master password
    reset_requested = pyqtSignal()  # User requested full reset
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Spacer at top
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Center container
        container = QFrame()
        container.setObjectName("headerFrame")
        container.setMaximumWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        
        # Logo/Title
        title = QLabel("NapishtimVault")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Enter your master password")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(subtitle)
        
        container_layout.addSpacing(20)
        
        # Password field
        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Master password")
        self.password_input.returnPressed.connect(self._on_submit)
        pwd_row.addWidget(self.password_input, 1)

        self.show_pwd_btn = QPushButton("👁")
        self.show_pwd_btn.setObjectName("iconButton")
        self.show_pwd_btn.setToolTip("Show/Hide password")
        self.show_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_pwd_btn.clicked.connect(self._toggle_password_visibility)
        pwd_row.addWidget(self.show_pwd_btn)

        container_layout.addLayout(pwd_row)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        container_layout.addWidget(self.error_label)
        
        container_layout.addSpacing(10)
        
        # Submit button
        self.submit_btn = QPushButton("Unlock")
        self.submit_btn.setObjectName("primaryButton")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._on_submit)
        container_layout.addWidget(self.submit_btn)

        # Reset vault button
        self.reset_btn = QPushButton("Reset Vault")
        self.reset_btn.setObjectName("dangerButton")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._on_reset)
        container_layout.addWidget(self.reset_btn)
        
        # Center the container
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(container)
        h_layout.addStretch()
        layout.addLayout(h_layout)
        
        # Spacer at bottom
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Focus password field
        self.password_input.setFocus()
    
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
    
    def _hide_error(self):
        self.error_label.hide()
    
    def _on_submit(self):
        self._hide_error()
        
        password = self.password_input.text()
        
        if not password:
            self._show_error("Password is required")
            return
        
        self.login_success.emit(password)

    def _on_reset(self):
        self._hide_error()
        self.reset_requested.emit()

    def _toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pwd_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pwd_btn.setText("👁")
    
    def show_error(self, message: str):
        """Show an error message (called from outside)."""
        self._show_error(message)
        self.password_input.clear()
        self.password_input.setFocus()
    
    def clear(self):
        """Clear input fields."""
        self.password_input.clear()
        self._hide_error()
        self.password_input.setFocus()
