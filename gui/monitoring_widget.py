"""
📊 Monitoring Widget - Real-time Statistics and Logs
Date: 03/09/2025
Description: Real-time monitoring of display communications and statistics
"""

from datetime import datetime
from typing import List, Dict

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
        QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
        QHeaderView, QSplitter
    )
    from PySide6.QtCore import Qt, QTimer
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
        QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
        QHeaderView, QSplitter
    )
    from PyQt6.QtCore import Qt, QTimer

from core.serial_emulator import SerialEmulator


class MonitoringWidget(QWidget):
    """Real-time monitoring widget"""
    
    def __init__(self, serial_emulator: SerialEmulator):
        super().__init__()
        self.serial_emulator = serial_emulator
        self.communication_log: List[Dict] = []
        
        self.setup_ui()
        self.setup_monitoring()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup monitoring UI"""
        layout = QVBoxLayout(self)
        
        # Statistics section
        stats_group = QGroupBox("Statistiques en Temps Réel")
        stats_layout = QHBoxLayout(stats_group)
        
        # Messages statistics
        self.total_messages_label = QLabel("Messages: 0")
        self.successful_messages_label = QLabel("Succès: 0")
        self.failed_messages_label = QLabel("Échecs: 0")
        self.avg_latency_label = QLabel("Latence moy: 0ms")
        
        stats_layout.addWidget(self.total_messages_label)
        stats_layout.addWidget(self.successful_messages_label)
        stats_layout.addWidget(self.failed_messages_label)
        stats_layout.addWidget(self.avg_latency_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_group)
        
        # Splitter for communications table and log
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Communications table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        table_controls = QHBoxLayout()
        table_controls.addWidget(QLabel("Journal des Communications"))
        table_controls.addStretch()
        
        clear_table_btn = QPushButton("Vider")
        clear_table_btn.clicked.connect(self.clear_table)
        table_controls.addWidget(clear_table_btn)
        
        table_layout.addLayout(table_controls)
        
        self.communications_table = QTableWidget()
        self.communications_table.setColumnCount(5)
        self.communications_table.setHorizontalHeaderLabels([
            "Heure", "Port", "Direction", "Données", "Statut"
        ])
        
        # Auto-resize columns
        header = self.communications_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        table_layout.addWidget(self.communications_table)
        splitter.addWidget(table_widget)
        
        # Log text area
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        log_controls = QHBoxLayout()
        log_controls.addWidget(QLabel("Log Détaillé"))
        log_controls.addStretch()
        
        clear_log_btn = QPushButton("Vider")
        clear_log_btn.clicked.connect(self.clear_log)
        log_controls.addWidget(clear_log_btn)
        
        log_layout.addLayout(log_controls)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 150])
    
    def setup_monitoring(self):
        """Setup monitoring event handlers"""
        self.serial_emulator.on('port-opened', self.on_port_opened)
        self.serial_emulator.on('port-closed', self.on_port_closed)
        self.serial_emulator.on('message-sent', self.on_message_sent)
        self.serial_emulator.on('message-failed', self.on_message_failed)
        self.serial_emulator.on('port-created', self.on_port_created)
    
    def update_statistics(self):
        """Update statistics display"""
        stats = self.serial_emulator.get_statistics()
        
        self.total_messages_label.setText(f"Messages: {stats.get('total_messages', 0)}")
        self.successful_messages_label.setText(f"Succès: {stats.get('successful_messages', 0)}")
        self.failed_messages_label.setText(f"Échecs: {stats.get('failed_messages', 0)}")
        self.avg_latency_label.setText(f"Latence moy: {stats.get('average_latency', 0):.1f}ms")
    
    def add_communication_entry(self, timestamp: datetime, port_name: str, 
                              direction: str, data: str, status: str):
        """Add entry to communications table"""
        row = self.communications_table.rowCount()
        self.communications_table.insertRow(row)
        
        # Limit table size
        if row >= 1000:
            self.communications_table.removeRow(0)
            row -= 1
        
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        
        self.communications_table.setItem(row, 0, QTableWidgetItem(time_str))
        self.communications_table.setItem(row, 1, QTableWidgetItem(port_name))
        self.communications_table.setItem(row, 2, QTableWidgetItem("📤" if direction == "out" else "📥"))
        self.communications_table.setItem(row, 3, QTableWidgetItem(data[:50] + "..." if len(data) > 50 else data))
        
        # Status with color
        status_item = QTableWidgetItem(status)
        if status == "success":
            status_item.setText("✅ Succès")
        elif status == "error":
            status_item.setText("❌ Erreur")
        elif status == "timeout":
            status_item.setText("⏱️ Timeout")
        
        self.communications_table.setItem(row, 4, status_item)
        
        # Scroll to bottom
        self.communications_table.scrollToBottom()
    
    def add_log_entry(self, message: str):
        """Add entry to detailed log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Limit log size
        if self.log_text.document().lineCount() > 1000:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 100)
            cursor.removeSelectedText()
    
    def clear_table(self):
        """Clear communications table"""
        self.communications_table.setRowCount(0)
        self.communication_log.clear()
    
    def clear_log(self):
        """Clear detailed log"""
        self.log_text.clear()
    
    def clear_logs(self):
        """Clear all logs (called from main window)"""
        self.clear_table()
        self.clear_log()
    
    # Event handlers
    def on_port_created(self, data: dict):
        """Handle port created event"""
        port_name = data.get('port_name', 'Unknown')
        conn_type = data.get('connection_type', 'unknown')
        self.add_log_entry(f"🔧 Port {port_name} créé ({conn_type})")
    
    def on_port_opened(self, data: dict):
        """Handle port opened event"""
        port_name = data.get('port_name', 'Unknown')
        self.add_log_entry(f"🟢 Port {port_name} ouvert")
        
        timestamp = data.get('timestamp', datetime.now())
        self.add_communication_entry(timestamp, port_name, "system", "Connexion établie", "success")
    
    def on_port_closed(self, data: dict):
        """Handle port closed event"""
        port_name = data.get('port_name', 'Unknown')
        self.add_log_entry(f"🔴 Port {port_name} fermé")
        
        timestamp = data.get('timestamp', datetime.now())
        self.add_communication_entry(timestamp, port_name, "system", "Connexion fermée", "success")
    
    def on_message_sent(self, data: dict):
        """Handle message sent event"""
        port_name = data.get('port_name', 'Unknown')
        message = data.get('data', '')
        timestamp_str = data.get('timestamp')
        
        if isinstance(timestamp_str, str):
            # Parse timestamp if it's a string
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        else:
            timestamp = timestamp_str or datetime.now()
        
        self.add_log_entry(f"📤 Message envoyé vers {port_name}: {message[:50]}")
        self.add_communication_entry(timestamp, port_name, "out", message, "success")
    
    def on_message_failed(self, data: dict):
        """Handle message failed event"""
        comm_data = data.get('communication', {})
        error = data.get('error')
        
        port_name = comm_data.get('port_name', 'Unknown')
        message = comm_data.get('data', '')
        
        self.add_log_entry(f"❌ Échec envoi vers {port_name}: {str(error)}")
        
        timestamp = comm_data.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        
        self.add_communication_entry(timestamp, port_name, "out", message, "error")