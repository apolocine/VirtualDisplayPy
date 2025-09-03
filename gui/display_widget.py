"""
🖥️ Display Widget - Individual Virtual Display Component
Date: 03/09/2025
Description: Qt widget representing a single virtual display
"""

from typing import Optional
from datetime import datetime

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
        QFrame, QMenu, QMessageBox
    )
    from PySide6.QtCore import Qt, Signal, QTimer
    from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QContextMenuEvent
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
        QFrame, QMenu, QMessageBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal as Signal, QTimer
    from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor

from models.display_config import VirtualDisplay, ConnectionType, DISPLAY_THEMES
from core.serial_emulator import SerialEmulator
from core.display_renderer import DisplayRenderer


class VirtualDisplayWidget(QFrame):
    """Widget representing a single virtual display"""
    
    # Signals
    selected = Signal(str)  # display_id
    remove_requested = Signal(str)  # display_id
    
    def __init__(self, display: VirtualDisplay, serial_emulator: SerialEmulator, 
                 display_renderer: DisplayRenderer):
        super().__init__()
        
        self.display = display
        self.serial_emulator = serial_emulator
        self.display_renderer = display_renderer
        self.is_selected = False
        
        self.setup_ui()
        self.update_display()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(250)  # Update every 250ms
    
    def setup_ui(self):
        """Setup widget UI"""
        self.setFrameStyle(QFrame.Box)
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            VirtualDisplayWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            VirtualDisplayWidget:hover {
                border-color: #aaa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header with port name and status
        header_layout = QHBoxLayout()
        
        self.port_label = QLabel(self.display.config.port_name)
        self.port_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(self.port_label)
        
        header_layout.addStretch()
        
        # Connection type indicator
        conn_type = self.display.config.connection_type
        if conn_type == ConnectionType.SERIAL:
            type_icon = "📟"
        elif conn_type == ConnectionType.USB:
            type_icon = "🔌"
        else:
            type_icon = "🌐"
        
        self.type_label = QLabel(type_icon)
        header_layout.addWidget(self.type_label)
        
        # Status indicator
        self.status_indicator = QLabel("🔴")
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        
        # Display screen
        self.screen_label = QLabel()
        self.screen_label.setMinimumHeight(120)
        self.screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screen_label.setStyleSheet("""
            QLabel {
                border: 1px solid #333;
                border-radius: 4px;
                background-color: #001100;
                color: #00ff00;
                font-family: monospace;
                font-size: 12px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.screen_label)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connecter")
        self.connect_btn.clicked.connect(self.toggle_connection)
        buttons_layout.addWidget(self.connect_btn)
        
        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(self.send_test_message)
        buttons_layout.addWidget(self.test_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_display)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addLayout(buttons_layout)
    
    def update_display(self):
        """Update display appearance"""
        # Update connection status
        if self.display.is_active:
            self.status_indicator.setText("🟢")
            self.connect_btn.setText("Déconnecter")
        else:
            self.status_indicator.setText("🔴")
            self.connect_btn.setText("Connecter")
        
        # Update display content
        content = self.display.current_content
        if content and any(line.strip() for line in content):
            display_text = "\n".join(content[:self.display.config.display_lines])
        else:
            display_text = "Afficheur Virtuel\n" + self.display.config.port_name
        
        self.screen_label.setText(display_text)
        
        # Update theme colors
        theme_info = DISPLAY_THEMES.get(self.display.config.theme)
        if theme_info:
            colors = theme_info["colors"]
            self.screen_label.setStyleSheet(f"""
                QLabel {{
                    border: 1px solid #333;
                    border-radius: 4px;
                    background-color: {colors["bg"]};
                    color: {colors["text"]};
                    font-family: monospace;
                    font-size: {self.display.config.font_size}px;
                    padding: 8px;
                }}
            """)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                VirtualDisplayWidget {
                    border: 2px solid #0078d4;
                    border-radius: 8px;
                    background-color: #f0f8ff;
                }
            """)
        else:
            self.setStyleSheet("""
                VirtualDisplayWidget {
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                }
                VirtualDisplayWidget:hover {
                    border-color: #aaa;
                }
            """)
    
    def toggle_connection(self):
        """Toggle display connection"""
        import asyncio
        
        if self.display.is_active:
            # Disconnect
            asyncio.create_task(
                self.serial_emulator.close_port(self.display.config.port_name)
            )
        else:
            # Connect
            asyncio.create_task(
                self.serial_emulator.open_port(
                    self.display.config.port_name, self.display.config
                )
            )
    
    def send_test_message(self):
        """Send test message to display"""
        if not self.display.is_active:
            QMessageBox.warning(self, "Test", "Afficheur non connecté")
            return
        
        import asyncio
        
        test_message = f"Test {datetime.now().strftime('%H:%M:%S')}"
        asyncio.create_task(
            self.serial_emulator.send_message(
                self.display.config.port_name, test_message, self.display.config
            )
        )
    
    def clear_display(self):
        """Clear display content"""
        if not self.display.is_active:
            return
        
        import asyncio
        
        asyncio.create_task(
            self.serial_emulator.send_message(
                self.display.config.port_name, "", self.display.config
            )
        )
        
        self.display.current_content = [""] * self.display.config.display_lines
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.display.id)
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """Handle right-click context menu"""
        menu = QMenu(self)
        
        # Configuration action
        config_action = menu.addAction("⚙️ Configuration")
        config_action.triggered.connect(lambda: self.selected.emit(self.display.id))
        
        menu.addSeparator()
        
        # Test actions
        test_action = menu.addAction("🧪 Test Message")
        test_action.triggered.connect(self.send_test_message)
        test_action.setEnabled(self.display.is_active)
        
        clear_action = menu.addAction("🗑️ Effacer")
        clear_action.triggered.connect(self.clear_display)
        clear_action.setEnabled(self.display.is_active)
        
        menu.addSeparator()
        
        # Remove action
        remove_action = menu.addAction("❌ Supprimer")
        remove_action.triggered.connect(self.confirm_remove)
        
        menu.exec_(event.globalPos())
    
    def confirm_remove(self):
        """Confirm display removal"""
        reply = QMessageBox.question(
            self, "Supprimer Afficheur",
            f"Voulez-vous vraiment supprimer l'afficheur {self.display.config.port_name} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.remove_requested.emit(self.display.id)