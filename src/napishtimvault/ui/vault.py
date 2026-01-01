"""Vault list UI."""

from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QSpacerItem, QSizePolicy, QMenu
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QAction, QCursor

from ..models import Credential


class CredentialListItem(QListWidgetItem):
    """Custom list item for credentials."""
    
    def __init__(self, credential: Credential):
        super().__init__()
        self.credential = credential
        self.setText(credential.title)
        self.setData(Qt.ItemDataRole.UserRole, credential.id)


class CredentialItemWidget(QFrame):
    """Custom widget for displaying a credential in the list."""
    
    copy_username = pyqtSignal(int)
    copy_password = pyqtSignal(int)
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    
    def __init__(self, credential: Credential, parent=None):
        super().__init__(parent)
        self.credential = credential
        self._init_ui()
    
    def _init_ui(self):
        self.setObjectName("credentialItem")
        self.setStyleSheet("""
            #credentialItem {
                background-color: #16213e;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 4px;
            }
            #credentialItem:hover {
                border-color: #e94560;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        title = QLabel(self.credential.title)
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #eaeaea;")
        info_layout.addWidget(title)
        
        username = QLabel(self.credential.username)
        username.setStyleSheet("font-size: 12px; color: #a0a0a0;")
        info_layout.addWidget(username)
        
        if self.credential.url:
            url = QLabel(self.credential.url)
            url.setStyleSheet("font-size: 11px; color: #707070;")
            info_layout.addWidget(url)
        
        layout.addLayout(info_layout, 1)
        
        # Buttons section
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        
        # Copy username button
        copy_user_btn = QPushButton("👤")
        copy_user_btn.setObjectName("iconButton")
        copy_user_btn.setToolTip("Copy username")
        copy_user_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_user_btn.clicked.connect(lambda: self.copy_username.emit(self.credential.id))
        btn_layout.addWidget(copy_user_btn)
        
        # Copy password button
        copy_pwd_btn = QPushButton("🔑")
        copy_pwd_btn.setObjectName("iconButton")
        copy_pwd_btn.setToolTip("Copy password")
        copy_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_pwd_btn.clicked.connect(lambda: self.copy_password.emit(self.credential.id))
        btn_layout.addWidget(copy_pwd_btn)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setObjectName("iconButton")
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.credential.id))
        btn_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setObjectName("iconButton")
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.credential.id))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)


class VaultWidget(QWidget):
    """Main vault view showing list of credentials."""
    
    add_clicked = pyqtSignal()
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    copy_username = pyqtSignal(int)
    copy_password = pyqtSignal(int)
    lock_clicked = pyqtSignal()
    change_master_password_clicked = pyqtSignal()
    history_clicked = pyqtSignal()
    search_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._credentials: List[Credential] = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(12)
        
        title = QLabel("🔐 Vault")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e94560;")
        header.addWidget(title)
        
        header.addStretch()

        # Change master password button
        change_pwd_btn = QPushButton("Change Master Password")
        change_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pwd_btn.setToolTip("Change the master password (re-encrypts all entries)")
        change_pwd_btn.clicked.connect(self.change_master_password_clicked.emit)
        header.addWidget(change_pwd_btn)

        # History button
        history_btn = QPushButton("History")
        history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        history_btn.setToolTip("View create/edit/delete history")
        history_btn.clicked.connect(self.history_clicked.emit)
        header.addWidget(history_btn)
        
        # Lock button
        lock_btn = QPushButton("🔒 Lock")
        lock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        lock_btn.setToolTip("Lock vault")
        lock_btn.clicked.connect(self.lock_clicked.emit)
        header.addWidget(lock_btn)
        
        layout.addLayout(header)
        
        # Search and Add row
        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        search_row.addWidget(self.search_input, 1)
        
        add_btn = QPushButton("+ Add")
        add_btn.setObjectName("primaryButton")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.add_clicked.emit)
        search_row.addWidget(add_btn)
        
        layout.addLayout(search_row)
        
        # Credentials list container
        self.list_container = QVBoxLayout()
        self.list_container.setSpacing(8)
        
        # Scroll area content
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.list_container)
        
        # We'll use a simple QVBoxLayout with widgets instead of QListWidget
        # for more flexible styling
        self.list_frame = QFrame()
        self.list_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        list_layout = QVBoxLayout(self.list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(8)
        self.list_layout = list_layout
        
        layout.addWidget(self.list_frame, 1)
        
        # Empty state label
        self.empty_label = QLabel("No credentials yet.\nClick '+ Add' to create your first entry.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #a0a0a0; font-size: 14px; padding: 40px;")
        layout.addWidget(self.empty_label)
        self.empty_label.hide()
        
        # Status bar
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #4ecca3; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        self.status_label.hide()
    
    def set_credentials(self, credentials: List[Credential]):
        """Update the displayed credentials."""
        self._credentials = credentials
        self._refresh_list()
    
    def _refresh_list(self):
        """Refresh the credentials list UI."""
        # Clear existing items
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self._credentials:
            self.empty_label.show()
            self.list_frame.hide()
            return
        
        self.empty_label.hide()
        self.list_frame.show()
        
        for cred in self._credentials:
            item_widget = CredentialItemWidget(cred)
            item_widget.copy_username.connect(self.copy_username.emit)
            item_widget.copy_password.connect(self.copy_password.emit)
            item_widget.edit_clicked.connect(self.edit_clicked.emit)
            item_widget.delete_clicked.connect(self.delete_clicked.emit)
            self.list_layout.addWidget(item_widget)
        
        # Add stretch at the end
        self.list_layout.addStretch()
    
    def show_status(self, message: str, duration_ms: int = 3000):
        """Show a temporary status message."""
        self.status_label.setText(message)
        self.status_label.show()
        
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(duration_ms, self.status_label.hide)
    
    def clear_search(self):
        """Clear the search input."""
        self.search_input.clear()
