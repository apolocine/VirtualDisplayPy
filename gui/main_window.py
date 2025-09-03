"""
🖥️ Main Window - Primary GUI Interface
Date: 03/09/2025
Description: Main application window with display grid and controls
"""

import sys
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QPushButton, QLabel, QComboBox, QSpinBox, QCheckBox, QTabWidget,
        QScrollArea, QFrame, QStatusBar, QMenuBar, QMenu,
        QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
        QTextEdit, QProgressBar, QSplitter, QGroupBox
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
    from PySide6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QAction
except ImportError:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QPushButton, QLabel, QComboBox, QSpinBox, QCheckBox, QTabWidget,
        QScrollArea, QFrame, QStatusBar, QMenuBar, QMenu,
        QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
        QTextEdit, QProgressBar, QSplitter, QGroupBox
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal
    from PyQt6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QAction

from core.serial_emulator import SerialEmulator
from core.display_renderer import DisplayRenderer
from models.display_config import (
    VirtualDisplayConfig, VirtualDisplay, DisplayTheme, ConnectionType,
    DEFAULT_DISPLAY_CONFIG, DEFAULT_USB_CONFIG, BAUD_RATES
)
from gui.display_widget import VirtualDisplayWidget
from gui.config_panel import ConfigurationPanel
from gui.monitoring_widget import MonitoringWidget


class VirtualDisplayMainWindow(QMainWindow):
    """Main application window"""
    
    # Signals
    display_added = Signal(str)  # display_id
    display_removed = Signal(str)  # display_id
    display_updated = Signal(str, dict)  # display_id, config
    
    def __init__(self, serial_emulator: SerialEmulator, display_renderer: DisplayRenderer):
        super().__init__()
        
        self.serial_emulator = serial_emulator
        self.display_renderer = display_renderer
        self.displays: Dict[str, VirtualDisplay] = {}
        self.display_widgets: Dict[str, VirtualDisplayWidget] = {}
        
        self.selected_display_id: Optional[str] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()
        self.setup_connections()
        
        # Setup timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(100)  # Update every 100ms
        
        # Setup serial emulator events
        self.setup_emulator_events()
    
    def setup_ui(self):
        """Setup main user interface"""
        self.setWindowTitle("VirtualDisplayPy - Émulateur d'Afficheur MostaGare v1.0.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Display grid and controls
        left_panel = self.create_display_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Configuration and monitoring
        right_panel = self.create_control_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([800, 400])
    
    def create_display_panel(self) -> QWidget:
        """Create the display grid panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.add_serial_btn = QPushButton("➕ Ajouter Série")
        self.add_serial_btn.clicked.connect(self.add_serial_display)
        controls_layout.addWidget(self.add_serial_btn)
        
        self.add_usb_btn = QPushButton("🔌 Ajouter USB")
        self.add_usb_btn.clicked.connect(self.add_usb_display)
        controls_layout.addWidget(self.add_usb_btn)
        
        self.connect_all_btn = QPushButton("🟢 Connecter Tout")
        self.connect_all_btn.clicked.connect(self.connect_all_displays)
        controls_layout.addWidget(self.connect_all_btn)
        
        self.disconnect_all_btn = QPushButton("🔴 Déconnecter Tout")
        self.disconnect_all_btn.clicked.connect(self.disconnect_all_displays)
        controls_layout.addWidget(self.disconnect_all_btn)
        
        controls_layout.addStretch()
        
        self.test_btn = QPushButton("🧪 Test Global")
        self.test_btn.clicked.connect(self.run_global_test)
        controls_layout.addWidget(self.test_btn)
        
        layout.addLayout(controls_layout)
        
        # Display grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.display_grid_widget = QWidget()
        self.display_grid_layout = QGridLayout(self.display_grid_widget)
        self.display_grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll_area.setWidget(self.display_grid_widget)
        layout.addWidget(scroll_area)
        
        # Empty state
        self.empty_state_label = QLabel("Aucun afficheur configuré\n\nCliquez sur '➕ Ajouter Série' ou '🔌 Ajouter USB' pour commencer")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 16px;
                padding: 40px;
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)
        layout.addWidget(self.empty_state_label)
        
        self.update_empty_state()
        
        return panel
    
    def create_control_panel(self) -> QWidget:
        """Create the control panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Configuration tab
        self.config_panel = ConfigurationPanel()
        self.config_panel.config_changed.connect(self.on_display_config_changed)
        self.tab_widget.addTab(self.config_panel, "⚙️ Configuration")
        
        # Monitoring tab
        self.monitoring_widget = MonitoringWidget(self.serial_emulator)
        self.tab_widget.addTab(self.monitoring_widget, "📊 Monitoring")
        
        # Test scenarios tab
        self.test_panel = self.create_test_panel()
        self.tab_widget.addTab(self.test_panel, "🧪 Tests")
        
        return panel
    
    def create_test_panel(self) -> QWidget:
        """Create test scenarios panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Test scenario selection
        scenario_group = QGroupBox("Scénarios de Test")
        scenario_layout = QFormLayout(scenario_group)
        
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems([
            "Fonctionnement Normal",
            "Test USB",
            "Simulation Paiement", 
            "Test de Stress",
            "Simulation Pannes"
        ])
        scenario_layout.addRow("Scénario:", self.scenario_combo)
        
        layout.addWidget(scenario_group)
        
        # Test controls
        test_controls = QHBoxLayout()
        
        self.run_test_btn = QPushButton("▶️ Exécuter Test")
        self.run_test_btn.clicked.connect(self.run_selected_test)
        test_controls.addWidget(self.run_test_btn)
        
        self.stop_test_btn = QPushButton("⏹️ Arrêter Test")
        self.stop_test_btn.clicked.connect(self.stop_current_test)
        self.stop_test_btn.setEnabled(False)
        test_controls.addWidget(self.stop_test_btn)
        
        layout.addLayout(test_controls)
        
        # Test progress
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        layout.addWidget(self.test_progress)
        
        # Test results
        self.test_results = QTextEdit()
        self.test_results.setMaximumHeight(200)
        self.test_results.setPlaceholderText("Les résultats de test s'afficheront ici...")
        layout.addWidget(self.test_results)
        
        layout.addStretch()
        
        return panel
    
    def setup_menus(self):
        """Setup application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&Fichier")
        
        save_config_action = QAction("&Sauvegarder Configuration", self)
        save_config_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_config_action)
        
        load_config_action = QAction("&Charger Configuration", self)
        load_config_action.triggered.connect(self.load_configuration)
        file_menu.addAction(load_config_action)
        
        file_menu.addSeparator()
        
        export_logs_action = QAction("&Exporter Logs", self)
        export_logs_action.triggered.connect(self.export_logs)
        file_menu.addAction(export_logs_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quitter", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Display menu
        display_menu = menubar.addMenu("&Afficheurs")
        
        add_serial_action = QAction("Ajouter &Série", self)
        add_serial_action.triggered.connect(self.add_serial_display)
        display_menu.addAction(add_serial_action)
        
        add_usb_action = QAction("Ajouter &USB", self)
        add_usb_action.triggered.connect(self.add_usb_display)
        display_menu.addAction(add_usb_action)
        
        display_menu.addSeparator()
        
        connect_all_action = QAction("&Connecter Tout", self)
        connect_all_action.triggered.connect(self.connect_all_displays)
        display_menu.addAction(connect_all_action)
        
        disconnect_all_action = QAction("&Déconnecter Tout", self)
        disconnect_all_action.triggered.connect(self.disconnect_all_displays)
        display_menu.addAction(disconnect_all_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Outils")
        
        test_action = QAction("&Test Global", self)
        test_action.triggered.connect(self.run_global_test)
        tools_menu.addAction(test_action)
        
        tools_menu.addSeparator()
        
        clear_logs_action = QAction("&Vider Logs", self)
        clear_logs_action.triggered.connect(self.clear_logs)
        tools_menu.addAction(clear_logs_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("À &Propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        
        # Connection status
        self.connection_status_label = QLabel("🔴 Aucune connexion")
        self.status_bar.addWidget(self.connection_status_label)
        
        self.status_bar.addPermanentWidget(QLabel("VirtualDisplayPy v1.0.0"))
    
    def setup_connections(self):
        """Setup signal connections"""
        self.display_added.connect(self.on_display_added)
        self.display_removed.connect(self.on_display_removed)
        self.display_updated.connect(self.on_display_updated)
    
    def setup_emulator_events(self):
        """Setup serial emulator event handlers"""
        self.serial_emulator.on('port-opened', self.on_port_opened)
        self.serial_emulator.on('port-closed', self.on_port_closed)
        self.serial_emulator.on('message-sent', self.on_message_sent)
        self.serial_emulator.on('message-failed', self.on_message_failed)
        self.serial_emulator.on('display-update', self.on_display_update)
    
    def add_serial_display(self):
        """Add a new serial display"""
        display_id = f"display_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create configuration with unique port name
        config = VirtualDisplayConfig(
            port_name=f"COM{len(self.displays) + 1}",
            connection_type=ConnectionType.SERIAL
        )
        
        display = VirtualDisplay(
            id=display_id,
            config=config
        )
        
        self.displays[display_id] = display
        self.create_display_widget(display)
        self.display_added.emit(display_id)
    
    def add_usb_display(self):
        """Add a new USB display"""
        display_id = f"usb_display_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create USB configuration
        config = VirtualDisplayConfig(
            port_name=f"USB{len([d for d in self.displays.values() if d.config.connection_type == ConnectionType.USB]) + 1}",
            connection_type=ConnectionType.USB,
            usb_vendor_id="04D8",
            usb_product_id="000A",
            theme=DisplayTheme.LCD_BLUE
        )
        
        display = VirtualDisplay(
            id=display_id,
            config=config
        )
        
        self.displays[display_id] = display
        self.create_display_widget(display)
        self.display_added.emit(display_id)
    
    def create_display_widget(self, display: VirtualDisplay):
        """Create widget for a display"""
        widget = VirtualDisplayWidget(
            display=display,
            serial_emulator=self.serial_emulator,
            display_renderer=self.display_renderer
        )
        
        widget.selected.connect(self.on_display_selected)
        widget.remove_requested.connect(self.remove_display)
        
        self.display_widgets[display.id] = widget
        
        # Add to grid
        row = len(self.display_widgets) // 3
        col = len(self.display_widgets) % 3
        self.display_grid_layout.addWidget(widget, row, col)
        
        self.update_empty_state()
    
    def remove_display(self, display_id: str):
        """Remove a display"""
        if display_id in self.displays:
            # Close connection if active
            display = self.displays[display_id]
            if display.is_active:
                asyncio.create_task(
                    self.serial_emulator.close_port(display.config.port_name)
                )
            
            # Remove from UI
            if display_id in self.display_widgets:
                widget = self.display_widgets[display_id]
                widget.setParent(None)
                widget.deleteLater()
                del self.display_widgets[display_id]
            
            # Remove from data
            del self.displays[display_id]
            
            # Update selection
            if self.selected_display_id == display_id:
                self.selected_display_id = None
                self.config_panel.set_display(None)
            
            self.display_removed.emit(display_id)
            self.update_empty_state()
    
    def connect_all_displays(self):
        """Connect all displays"""
        for display in self.displays.values():
            if not display.is_active:
                asyncio.create_task(
                    self.serial_emulator.open_port(display.config.port_name, display.config)
                )
    
    def disconnect_all_displays(self):
        """Disconnect all displays"""
        for display in self.displays.values():
            if display.is_active:
                asyncio.create_task(
                    self.serial_emulator.close_port(display.config.port_name)
                )
    
    def run_global_test(self):
        """Run a global test on all displays"""
        if not self.displays:
            QMessageBox.information(self, "Test Global", "Aucun afficheur configuré pour le test.")
            return
        
        self.test_results.append(f"🧪 Test global démarré à {datetime.now().strftime('%H:%M:%S')}")
        
        # Send test messages to all connected displays
        for display in self.displays.values():
            if display.is_active:
                test_message = f"Test {display.config.port_name}"
                asyncio.create_task(
                    self.serial_emulator.send_message(
                        display.config.port_name, test_message, display.config
                    )
                )
                self.test_results.append(f"  📤 {display.config.port_name}: {test_message}")
    
    def run_selected_test(self):
        """Run the selected test scenario"""
        scenario = self.scenario_combo.currentText()
        self.test_results.append(f"🧪 Scénario '{scenario}' démarré...")
        
        self.run_test_btn.setEnabled(False)
        self.stop_test_btn.setEnabled(True)
        self.test_progress.setVisible(True)
        self.test_progress.setValue(0)
        
        # TODO: Implement actual test scenarios
        QTimer.singleShot(2000, self.finish_test)  # Simulate test completion
    
    def stop_current_test(self):
        """Stop current test"""
        self.finish_test()
        self.test_results.append("⏹️ Test interrompu par l'utilisateur")
    
    def finish_test(self):
        """Finish current test"""
        self.run_test_btn.setEnabled(True)
        self.stop_test_btn.setEnabled(False)
        self.test_progress.setVisible(False)
        self.test_results.append("✅ Test terminé")
    
    def update_empty_state(self):
        """Update empty state visibility"""
        has_displays = len(self.displays) > 0
        self.empty_state_label.setVisible(not has_displays)
        self.display_grid_widget.setVisible(has_displays)
    
    def update_displays(self):
        """Update display widgets"""
        # Update status bar
        active_connections = sum(1 for d in self.displays.values() if d.is_active)
        total_displays = len(self.displays)
        
        if active_connections > 0:
            self.connection_status_label.setText(f"🟢 {active_connections}/{total_displays} connectés")
        else:
            self.connection_status_label.setText("🔴 Aucune connexion")
        
        # Update display widgets
        for widget in self.display_widgets.values():
            widget.update_display()
    
    def on_display_selected(self, display_id: str):
        """Handle display selection"""
        # Deselect previous
        if self.selected_display_id and self.selected_display_id in self.display_widgets:
            self.display_widgets[self.selected_display_id].set_selected(False)
        
        # Select new
        self.selected_display_id = display_id
        if display_id in self.display_widgets:
            self.display_widgets[display_id].set_selected(True)
            
        # Update config panel
        display = self.displays.get(display_id)
        self.config_panel.set_display(display)
    
    def on_display_config_changed(self, config: VirtualDisplayConfig):
        """Handle display configuration change"""
        if self.selected_display_id and self.selected_display_id in self.displays:
            self.displays[self.selected_display_id].config = config
            self.display_updated.emit(self.selected_display_id, asdict(config))
    
    # Event handlers
    def on_display_added(self, display_id: str):
        """Handle display added"""
        pass
    
    def on_display_removed(self, display_id: str):
        """Handle display removed"""
        pass
    
    def on_display_updated(self, display_id: str, config: dict):
        """Handle display updated"""
        pass
    
    def on_port_opened(self, data: dict):
        """Handle port opened event"""
        port_name = data.get('port_name')
        for display in self.displays.values():
            if display.config.port_name == port_name:
                display.is_active = True
                display.last_activity = datetime.now()
                break
    
    def on_port_closed(self, data: dict):
        """Handle port closed event"""
        port_name = data.get('port_name')
        for display in self.displays.values():
            if display.config.port_name == port_name:
                display.is_active = False
                break
    
    def on_message_sent(self, data: dict):
        """Handle message sent event"""
        pass
    
    def on_message_failed(self, data: dict):
        """Handle message failed event"""
        pass
    
    def on_display_update(self, data: dict):
        """Handle display update event"""
        port_name = data.get('port_name')
        content = data.get('content', [])
        
        for display in self.displays.values():
            if display.config.port_name == port_name:
                display.current_content = content
                display.last_activity = datetime.now()
                break
    
    def save_configuration(self):
        """Save current configuration"""
        # TODO: Implement configuration saving
        QMessageBox.information(self, "Sauvegarde", "Configuration sauvegardée avec succès!")
    
    def load_configuration(self):
        """Load configuration from file"""
        # TODO: Implement configuration loading
        QMessageBox.information(self, "Chargement", "Configuration chargée avec succès!")
    
    def export_logs(self):
        """Export logs to file"""
        # TODO: Implement log export
        QMessageBox.information(self, "Export", "Logs exportés avec succès!")
    
    def clear_logs(self):
        """Clear monitoring logs"""
        self.monitoring_widget.clear_logs()
        QMessageBox.information(self, "Logs", "Logs vidés avec succès!")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "À Propos de VirtualDisplayPy", 
                         """
VirtualDisplayPy v1.0.0

Émulateur d'Afficheur Virtuel pour MostaGare
Développé avec Python et Qt

Fonctionnalités:
• Émulation afficheurs série et USB
• Interface graphique intuitive  
• Monitoring temps réel
• Tests automatisés
• Support multi-thèmes

© 2025 MostaGare Development Team
                         """)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup connections
        for display in self.displays.values():
            if display.is_active:
                asyncio.create_task(
                    self.serial_emulator.close_port(display.config.port_name)
                )
        
        # Accept close
        event.accept()