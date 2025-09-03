#!/usr/bin/env python3
"""
🖥️ VirtualDisplayPy - Simple GUI Demo
Date: 03/09/2025
Description: Simple working GUI demo for VirtualDisplayPy
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit, QGroupBox, QMessageBox
    )
    from PySide6.QtCore import Qt, QTimer, Signal
    from PySide6.QtGui import QFont
    QT_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QPushButton, QLabel, QTextEdit, QGroupBox, QMessageBox
        )
        from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal
        from PyQt6.QtGui import QFont
        QT_AVAILABLE = True
    except ImportError:
        QT_AVAILABLE = False

if QT_AVAILABLE:
    from core.serial_emulator import SerialEmulator
    from core.display_renderer import DisplayRenderer
    from models.display_config import VirtualDisplayConfig, ConnectionType, DisplayTheme

class SimpleVirtualDisplayGUI(QMainWindow):
    """Simple GUI for VirtualDisplayPy demonstration"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VirtualDisplayPy - Émulateur d'Afficheur")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize core components
        self.serial_emulator = SerialEmulator()
        self.display_renderer = DisplayRenderer()
        self.current_displays = {}
        
        # Setup message reception from external apps
        self.setup_external_message_listener()
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)
    
    def setup_ui(self):
        """Setup the UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🖥️ VirtualDisplayPy - Émulateur d'Afficheur MostaGare")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header)
        
        # Controls
        controls_group = QGroupBox("Contrôles")
        controls_layout = QHBoxLayout(controls_group)
        
        self.create_serial_btn = QPushButton("📟 Créer Afficheur Série")
        self.create_serial_btn.clicked.connect(self.create_serial_display)
        controls_layout.addWidget(self.create_serial_btn)
        
        self.create_usb_btn = QPushButton("🔌 Créer Afficheur USB")
        self.create_usb_btn.clicked.connect(self.create_usb_display)
        controls_layout.addWidget(self.create_usb_btn)
        
        self.create_usb_serial_btn = QPushButton("🔗 Créer USB-Série")
        self.create_usb_serial_btn.clicked.connect(self.create_usb_serial_display)
        controls_layout.addWidget(self.create_usb_serial_btn)
        
        self.test_btn = QPushButton("🧪 Test Message")
        self.test_btn.clicked.connect(self.send_test_message)
        controls_layout.addWidget(self.test_btn)
        
        self.clear_btn = QPushButton("🗑️ Effacer")
        self.clear_btn.clicked.connect(self.clear_displays)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addWidget(controls_group)
        
        # Status
        status_group = QGroupBox("État du Système")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Système initialisé - Aucun afficheur")
        self.status_label.setFont(QFont("Courier", 10))
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
        # Display Content
        displays_group = QGroupBox("Contenu des Afficheurs")
        displays_layout = QVBoxLayout(displays_group)
        
        self.displays_content = QTextEdit()
        self.displays_content.setMaximumHeight(150)
        self.displays_content.setFont(QFont("Courier", 9))
        self.displays_content.setStyleSheet("QTextEdit { background-color: #001100; color: #00ff00; }")
        displays_layout.addWidget(self.displays_content)
        
        layout.addWidget(displays_group)
        
        # Log
        log_group = QGroupBox("Journal d'Activité")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Courier", 9))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Add some initial messages
        self.log_message("✅ VirtualDisplayPy démarré avec succès")
        self.log_message("📟 Émulateur série initialisé")
        self.log_message("🎨 Moteur de rendu initialisé")
        self.log_message("🚀 Prêt à créer des afficheurs virtuels")
    
    def log_message(self, message: str):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def create_serial_display(self):
        """Create a serial display"""
        config = VirtualDisplayConfig(
            port_name="COM_SERIAL",
            connection_type=ConnectionType.SERIAL,
            baud_rate=9600,
            display_lines=2,
            line_length=20,
            theme=DisplayTheme.LCD_GREEN
        )
        
        self.create_display_sync(config)
    
    def create_usb_display(self):
        """Create a USB display"""
        config = VirtualDisplayConfig(
            port_name="USB_DISPLAY",
            connection_type=ConnectionType.USB,
            display_lines=2,
            line_length=16,
            theme=DisplayTheme.LCD_BLUE,
            usb_vendor_id="04D8",
            usb_product_id="000A"
        )
        
        self.create_display_sync(config)
    
    def create_usb_serial_display(self):
        """Create a USB-Serial display"""
        config = VirtualDisplayConfig(
            port_name="USB_SERIAL",
            connection_type=ConnectionType.USB_SERIAL,
            baud_rate=9600,
            display_lines=2,
            line_length=20,
            theme=DisplayTheme.VFD_CYAN,
            usb_vendor_id="0403",  # FTDI
            usb_product_id="6001"   # FT232R
        )
        
        self.create_display_sync(config)
    
    def create_display_sync(self, config: VirtualDisplayConfig):
        """Create display synchronously"""
        try:
            # Create virtual port
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                self.serial_emulator.create_virtual_port(config)
            )
            
            if success:
                self.log_message(f"✅ Port {config.port_name} créé ({config.connection_type.value})")
                
                # Open port
                loop.run_until_complete(
                    self.serial_emulator.open_port(config.port_name, config)
                )
                self.current_displays[config.port_name] = config
                self.log_message(f"🔌 Port {config.port_name} ouvert")
                
                self.update_status()
            else:
                self.log_message(f"❌ Échec création port {config.port_name}")
                
            loop.close()
        except Exception as e:
            self.log_message(f"💥 Erreur: {str(e)}")
    
    def send_test_message(self):
        """Send test message to all displays"""
        if not self.current_displays:
            QMessageBox.information(self, "Test", "Aucun afficheur disponible")
            return
        
        from datetime import datetime
        
        message = f"Test {datetime.now().strftime('%H:%M:%S')}"
        
        for port_name, config in self.current_displays.items():
            self.send_message_sync(port_name, message, config)
    
    def send_message_sync(self, port_name: str, message: str, config: VirtualDisplayConfig):
        """Send message synchronously"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            loop.run_until_complete(
                self.serial_emulator.send_message(port_name, message, config)
            )
            self.log_message(f"📤 Message envoyé vers {port_name}: {message}")
            loop.close()
        except Exception as e:
            self.log_message(f"❌ Erreur envoi vers {port_name}: {str(e)}")
    
    def clear_displays(self):
        """Clear all displays"""        
        for port_name, config in self.current_displays.items():
            self.send_message_sync(port_name, "", config)
        
        self.log_message("🗑️ Tous les afficheurs effacés")
    
    def update_status(self):
        """Update status display"""
        count = len(self.current_displays)
        if count == 0:
            status = "Aucun afficheur connecté"
        else:
            ports = ", ".join(self.current_displays.keys())
            status = f"{count} afficheur(s) connecté(s): {ports}"
        
        # Get statistics
        stats = self.serial_emulator.get_statistics()
        status += f" | Messages: {stats.get('total_messages', 0)}"
        status += f" | Succès: {stats.get('successful_messages', 0)}"
        status += f" | Latence: {stats.get('average_latency', 0):.1f}ms"
        
        self.status_label.setText(status)
        
        # Update display content
        content_text = ""
        for port_name in self.current_displays.keys():
            display_content = self.serial_emulator.get_display_content(port_name)
            if display_content and any(line.strip() for line in display_content):
                content_text += f"📟 {port_name}:\n"
                for line in display_content:
                    content_text += f"  {line}\n"
                content_text += "\n"
        
        if not content_text:
            content_text = "Aucun message affiché sur les displays"
        
        self.displays_content.setPlainText(content_text)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.serial_emulator.destroy()
        self.display_renderer.clear_cache()
        event.accept()
    
    def setup_external_message_listener(self):
        """Setup listener for external messages"""
        import tempfile
        import os
        
        # Create message file path
        self.message_file = os.path.join(tempfile.gettempdir(), "virtualdisplay_messages.txt")
        
        # File watcher timer
        self.file_watcher_timer = QTimer()
        self.file_watcher_timer.timeout.connect(self.check_external_messages)
        self.file_watcher_timer.start(500)  # Check every 500ms
        
        # Track last modification time
        self.last_message_mtime = 0
    
    def check_external_messages(self):
        """Check for new external messages"""
        import os
        
        try:
            if not os.path.exists(self.message_file):
                return
            
            # Check if file was modified
            mtime = os.path.getmtime(self.message_file)
            if mtime <= self.last_message_mtime:
                return
            
            self.last_message_mtime = mtime
            
            # Read and process messages
            with open(self.message_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if content:
                lines = content.split('\n')
                for line in lines:
                    if '|' in line:
                        try:
                            port, message = line.split('|', 1)
                            self.process_external_message(port.strip(), message.strip())
                        except:
                            pass
                
                # Clear the file after processing
                open(self.message_file, 'w').close()
                
        except Exception as e:
            pass  # Silently ignore file access errors
    
    def process_external_message(self, port_name: str, message: str):
        """Process message from external application"""
        if port_name in self.current_displays:
            # Update the display content directly
            config = self.current_displays[port_name]
            
            # Store the message in the serial emulator
            lines = message.split('\n')
            if len(lines) > config.display_lines:
                lines = lines[:config.display_lines]
            
            # Pad with empty lines if needed
            while len(lines) < config.display_lines:
                lines.append("")
            
            # Truncate lines to display width
            for i, line in enumerate(lines):
                if len(line) > config.line_length:
                    lines[i] = line[:config.line_length]
            
            # Store in serial emulator
            self.serial_emulator.display_content[port_name] = lines
            
            # Log the message
            self.log_message(f"📥 Message externe reçu sur {port_name}: {message}")
            
            # Force update the display
            self.update_status()

def main():
    """Main entry point"""
    if not QT_AVAILABLE:
        print("❌ Qt non disponible. Installez PySide6 ou PyQt6")
        print("   pip install PySide6")
        return 1
    
    app = QApplication(sys.argv)
    app.setApplicationName("VirtualDisplayPy")
    
    window = SimpleVirtualDisplayGUI()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())