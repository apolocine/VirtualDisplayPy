"""
⚙️ Configuration Panel - Display Settings Interface
Date: 03/09/2025
Description: Configuration panel for virtual display settings
"""

from typing import Optional

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QFormLayout, QComboBox, QSpinBox,
        QCheckBox, QGroupBox, QSlider, QLabel, QLineEdit
    )
    from PySide6.QtCore import Qt, Signal
except ImportError:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QFormLayout, QComboBox, QSpinBox,
        QCheckBox, QGroupBox, QSlider, QLabel, QLineEdit
    )
    from PyQt6.QtCore import Qt, pyqtSignal as Signal

from models.display_config import VirtualDisplay, VirtualDisplayConfig, DisplayTheme, ConnectionType, BAUD_RATES


class ConfigurationPanel(QWidget):
    """Configuration panel for display settings"""
    
    config_changed = Signal(VirtualDisplayConfig)
    
    def __init__(self):
        super().__init__()
        self.current_display: Optional[VirtualDisplay] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup configuration UI"""
        layout = QVBoxLayout(self)
        
        # No display selected message
        self.no_display_label = QLabel("Sélectionnez un afficheur pour configurer ses paramètres")
        self.no_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_display_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.no_display_label)
        
        # Configuration form (initially hidden)
        self.config_widget = QWidget()
        self.config_widget.setVisible(False)
        layout.addWidget(self.config_widget)
        
        config_layout = QVBoxLayout(self.config_widget)
        
        # Basic configuration
        basic_group = QGroupBox("Configuration de Base")
        basic_layout = QFormLayout(basic_group)
        
        self.port_name_edit = QLineEdit()
        basic_layout.addRow("Port:", self.port_name_edit)
        
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItems(["Série", "USB", "Réseau"])
        basic_layout.addRow("Type:", self.connection_type_combo)
        
        self.baud_rate_combo = QComboBox()
        self.baud_rate_combo.addItems([str(rate) for rate in BAUD_RATES])
        basic_layout.addRow("Débit:", self.baud_rate_combo)
        
        config_layout.addWidget(basic_group)
        
        # Display configuration
        display_group = QGroupBox("Configuration d'Affichage")
        display_layout = QFormLayout(display_group)
        
        self.lines_spin = QSpinBox()
        self.lines_spin.setRange(1, 4)
        display_layout.addRow("Lignes:", self.lines_spin)
        
        self.length_spin = QSpinBox()
        self.length_spin.setRange(10, 80)
        display_layout.addRow("Longueur:", self.length_spin)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "LCD Vert", "LCD Bleu", "LED Rouge", "OLED Blanc", "VFD Cyan"
        ])
        display_layout.addRow("Thème:", self.theme_combo)
        
        config_layout.addWidget(display_group)
        
        # Visual settings
        visual_group = QGroupBox("Paramètres Visuels")
        visual_layout = QFormLayout(visual_group)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        visual_layout.addRow("Taille police:", self.font_size_spin)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        visual_layout.addRow("Luminosité:", self.brightness_slider)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 100)
        visual_layout.addRow("Contraste:", self.contrast_slider)
        
        config_layout.addWidget(visual_group)
        
        # Behavior settings
        behavior_group = QGroupBox("Comportement")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.clear_on_connect_check = QCheckBox("Effacer à la connexion")
        behavior_layout.addWidget(self.clear_on_connect_check)
        
        self.cursor_visible_check = QCheckBox("Curseur visible")
        behavior_layout.addWidget(self.cursor_visible_check)
        
        self.blinking_cursor_check = QCheckBox("Curseur clignotant")
        behavior_layout.addWidget(self.blinking_cursor_check)
        
        config_layout.addWidget(behavior_group)
        
        config_layout.addStretch()
        
        # Connect signals
        self.connect_signals()
    
    def connect_signals(self):
        """Connect configuration change signals"""
        self.port_name_edit.textChanged.connect(self.on_config_changed)
        self.connection_type_combo.currentTextChanged.connect(self.on_config_changed)
        self.baud_rate_combo.currentTextChanged.connect(self.on_config_changed)
        self.lines_spin.valueChanged.connect(self.on_config_changed)
        self.length_spin.valueChanged.connect(self.on_config_changed)
        self.theme_combo.currentTextChanged.connect(self.on_config_changed)
        self.font_size_spin.valueChanged.connect(self.on_config_changed)
        self.brightness_slider.valueChanged.connect(self.on_config_changed)
        self.contrast_slider.valueChanged.connect(self.on_config_changed)
        self.clear_on_connect_check.toggled.connect(self.on_config_changed)
        self.cursor_visible_check.toggled.connect(self.on_config_changed)
        self.blinking_cursor_check.toggled.connect(self.on_config_changed)
    
    def set_display(self, display: Optional[VirtualDisplay]):
        """Set the display to configure"""
        self.current_display = display
        
        if display is None:
            self.no_display_label.setVisible(True)
            self.config_widget.setVisible(False)
        else:
            self.no_display_label.setVisible(False)
            self.config_widget.setVisible(True)
            self.load_configuration(display.config)
    
    def load_configuration(self, config: VirtualDisplayConfig):
        """Load configuration into UI"""
        # Block signals while loading
        self.blockSignals(True)
        
        self.port_name_edit.setText(config.port_name)
        
        # Connection type
        if config.connection_type == ConnectionType.SERIAL:
            self.connection_type_combo.setCurrentText("Série")
        elif config.connection_type == ConnectionType.USB:
            self.connection_type_combo.setCurrentText("USB")
        else:
            self.connection_type_combo.setCurrentText("Réseau")
        
        self.baud_rate_combo.setCurrentText(str(config.baud_rate))
        self.lines_spin.setValue(config.display_lines)
        self.length_spin.setValue(config.line_length)
        
        # Theme
        theme_map = {
            DisplayTheme.LCD_GREEN: "LCD Vert",
            DisplayTheme.LCD_BLUE: "LCD Bleu",
            DisplayTheme.LED_RED: "LED Rouge",
            DisplayTheme.OLED_WHITE: "OLED Blanc",
            DisplayTheme.VFD_CYAN: "VFD Cyan"
        }
        self.theme_combo.setCurrentText(theme_map.get(config.theme, "LCD Vert"))
        
        self.font_size_spin.setValue(config.font_size)
        self.brightness_slider.setValue(config.brightness)
        self.contrast_slider.setValue(config.contrast)
        
        self.clear_on_connect_check.setChecked(config.clear_on_connect)
        self.cursor_visible_check.setChecked(config.cursor_visible)
        self.blinking_cursor_check.setChecked(config.blinking_cursor)
        
        self.blockSignals(False)
    
    def on_config_changed(self):
        """Handle configuration changes"""
        if not self.current_display:
            return
        
        # Create updated configuration
        config = self.current_display.config
        
        config.port_name = self.port_name_edit.text()
        
        # Connection type
        conn_text = self.connection_type_combo.currentText()
        if conn_text == "Série":
            config.connection_type = ConnectionType.SERIAL
        elif conn_text == "USB":
            config.connection_type = ConnectionType.USB
        else:
            config.connection_type = ConnectionType.NETWORK
        
        config.baud_rate = int(self.baud_rate_combo.currentText())
        config.display_lines = self.lines_spin.value()
        config.line_length = self.length_spin.value()
        
        # Theme
        theme_text = self.theme_combo.currentText()
        theme_map = {
            "LCD Vert": DisplayTheme.LCD_GREEN,
            "LCD Bleu": DisplayTheme.LCD_BLUE,
            "LED Rouge": DisplayTheme.LED_RED,
            "OLED Blanc": DisplayTheme.OLED_WHITE,
            "VFD Cyan": DisplayTheme.VFD_CYAN
        }
        config.theme = theme_map.get(theme_text, DisplayTheme.LCD_GREEN)
        
        config.font_size = self.font_size_spin.value()
        config.brightness = self.brightness_slider.value()
        config.contrast = self.contrast_slider.value()
        
        config.clear_on_connect = self.clear_on_connect_check.isChecked()
        config.cursor_visible = self.cursor_visible_check.isChecked()
        config.blinking_cursor = self.blinking_cursor_check.isChecked()
        
        # Emit change signal
        self.config_changed.emit(config)