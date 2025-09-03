"""
🖥️ Display Configuration Models
Date: 03/09/2025
Description: Configuration models for virtual displays
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class DisplayTheme(Enum):
    """Display visual themes"""
    LCD_GREEN = "lcd-green"
    LCD_BLUE = "lcd-blue"
    LED_RED = "led-red"
    OLED_WHITE = "oled-white"
    VFD_CYAN = "vfd-cyan"


class ConnectionStatus(Enum):
    """Connection status types"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    TIMEOUT = "timeout"
    CONNECTING = "connecting"


class FailureType(Enum):
    """Failure simulation types"""
    TIMEOUT = "timeout"
    DISCONNECT = "disconnect"
    CORRUPTION = "corruption"
    BUFFER_OVERFLOW = "buffer-overflow"
    CHECKSUM_ERROR = "checksum-error"


@dataclass
class DisplayMetrics:
    """Performance metrics for a virtual display"""
    # Communication metrics
    messages_received: int = 0
    messages_processed: int = 0
    messages_sent: int = 0
    bytes_received: int = 0
    bytes_sent: int = 0
    
    # Performance metrics
    avg_latency: float = 0.0
    min_latency: float = 0.0
    max_latency: float = 0.0
    
    # Error metrics
    total_errors: int = 0
    timeouts: int = 0
    connection_errors: int = 0
    protocol_errors: int = 0
    checksum_errors: int = 0
    
    # Time metrics
    connect_time: Optional[datetime] = None
    disconnect_time: Optional[datetime] = None
    total_uptime: float = 0.0
    last_reset_time: datetime = field(default_factory=datetime.now)


class ConnectionType(Enum):
    """Connection types supported"""
    SERIAL = "serial"
    USB = "usb"
    USB_SERIAL = "usb_serial"  # USB-to-Serial bridge (FTDI, CH340, etc.)
    NETWORK = "network"
    BLUETOOTH = "bluetooth"


@dataclass
class VirtualDisplayConfig:
    """Configuration for a virtual display"""
    # Basic configuration
    port_name: str = "COM1"
    connection_type: ConnectionType = ConnectionType.SERIAL
    baud_rate: int = 9600
    data_bits: Literal[5, 6, 7, 8] = 8
    stop_bits: Literal[1, 1.5, 2] = 1
    parity: Literal["none", "even", "odd", "mark", "space"] = "none"
    
    # USB specific configuration
    usb_vendor_id: Optional[str] = None
    usb_product_id: Optional[str] = None
    usb_serial_number: Optional[str] = None
    usb_interface: int = 0
    
    # Network specific configuration
    network_host: str = "localhost"
    network_port: int = 8080
    network_protocol: Literal["tcp", "udp"] = "tcp"
    
    # Display parameters
    display_lines: Literal[1, 2, 3, 4] = 2
    line_length: int = 20
    alignment: List[Literal["left", "center", "right"]] = field(default_factory=lambda: ["left", "left", "left", "left"])
    
    # Visual appearance
    theme: DisplayTheme = DisplayTheme.LCD_GREEN
    font_size: int = 14
    brightness: int = 80
    contrast: int = 75
    
    # Behavior
    clear_on_connect: bool = True
    cursor_visible: bool = False
    blinking_cursor: bool = False
    scrolling: bool = False
    
    # Error simulation
    artificial_latency: int = 0  # milliseconds
    error_rate: float = 0.0  # percentage
    simulated_failures: List[FailureType] = field(default_factory=list)
    
    # Timeouts
    connection_timeout: int = 5000  # milliseconds
    response_timeout: int = 3000  # milliseconds
    keep_alive_interval: int = 30000  # milliseconds


@dataclass
class VirtualDisplay:
    """Virtual display state and configuration"""
    id: str
    config: VirtualDisplayConfig
    
    # Current state
    is_active: bool = False
    connection_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    current_content: List[str] = field(default_factory=list)
    cursor_position: tuple[int, int] = (0, 0)  # (line, column)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    uptime: float = 0.0
    
    # Metrics
    metrics: DisplayMetrics = field(default_factory=DisplayMetrics)
    
    # Internal state
    buffer: List[str] = field(default_factory=list)
    command_queue: List[Dict[str, Any]] = field(default_factory=list)
    error_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize content and buffer arrays"""
        if not self.current_content:
            self.current_content = [""] * self.config.display_lines
        if not self.buffer:
            self.buffer = [""] * self.config.display_lines


@dataclass
class DisplayProfile:
    """Predefined display profiles"""
    name: str
    manufacturer: str
    model: str
    description: str
    
    # Technical specifications
    max_lines: int
    max_columns: int
    supported_baud_rates: List[int]
    supported_commands: List[str]
    
    # Default configuration
    default_config: Dict[str, Any]
    
    # Special features
    features: Dict[str, bool] = field(default_factory=lambda: {
        "graphics": False,
        "custom_characters": False,
        "backlight": True,
        "contrast": True,
        "cursor": True
    })


# Theme definitions
DISPLAY_THEMES = {
    DisplayTheme.LCD_GREEN: {
        "name": "LCD Vert Classique",
        "colors": {
            "bg": "#001100",
            "text": "#00ff00",
            "border": "#003300"
        }
    },
    DisplayTheme.LCD_BLUE: {
        "name": "LCD Bleu",
        "colors": {
            "bg": "#000011",
            "text": "#0088ff",
            "border": "#000033"
        }
    },
    DisplayTheme.LED_RED: {
        "name": "LED Rouge",
        "colors": {
            "bg": "#110000",
            "text": "#ff0000",
            "border": "#330000"
        }
    },
    DisplayTheme.OLED_WHITE: {
        "name": "OLED Blanc",
        "colors": {
            "bg": "#000000",
            "text": "#ffffff",
            "border": "#111111"
        }
    },
    DisplayTheme.VFD_CYAN: {
        "name": "VFD Cyan",
        "colors": {
            "bg": "#001111",
            "text": "#00ffff",
            "border": "#003333"
        }
    }
}

# Common baud rates
BAUD_RATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

# Common serial commands
COMMON_COMMANDS = {
    "CLEAR_SCREEN": "\x0C",
    "CARRIAGE_RETURN": "\r",
    "LINE_FEED": "\n",
    "NEW_LINE": "\r\n",
    "HOME": "\x1B[H",
    "CURSOR_POSITION": lambda line, col: f"\x1B[{line};{col}H",
    "CLEAR_LINE": "\x1B[K",
    "BACKSPACE": "\x08",
    "TAB": "\x09",
    "ESCAPE": "\x1B"
}

# Default display configuration
DEFAULT_DISPLAY_CONFIG = VirtualDisplayConfig(
    port_name="COM1",
    connection_type=ConnectionType.SERIAL,
    baud_rate=9600,
    data_bits=8,
    stop_bits=1,
    parity="none",
    display_lines=2,
    line_length=20,
    alignment=["left", "left", "left", "left"],
    theme=DisplayTheme.LCD_GREEN,
    font_size=14,
    brightness=80,
    contrast=75,
    clear_on_connect=True,
    cursor_visible=False,
    blinking_cursor=False,
    scrolling=False,
    artificial_latency=0,
    error_rate=0.0,
    simulated_failures=[],
    connection_timeout=5000,
    response_timeout=3000,
    keep_alive_interval=30000
)

# USB display configuration template
DEFAULT_USB_CONFIG = VirtualDisplayConfig(
    port_name="USB1",
    connection_type=ConnectionType.USB,
    usb_vendor_id="04D8",  # Microchip vendor ID (example)
    usb_product_id="000A",  # Product ID (example)
    display_lines=2,
    line_length=20,
    theme=DisplayTheme.LCD_BLUE,
    alignment=["left", "left", "left", "left"]
)

# USB-Serial bridge configuration template
DEFAULT_USB_SERIAL_CONFIG = VirtualDisplayConfig(
    port_name="USBSERIAL1",
    connection_type=ConnectionType.USB_SERIAL,
    baud_rate=9600,
    usb_vendor_id="0403",  # FTDI vendor ID
    usb_product_id="6001",  # FT232R USB UART
    display_lines=2,
    line_length=20,
    theme=DisplayTheme.LCD_GREEN,
    alignment=["left", "left", "left", "left"],
    # USB-Serial specific parameters
    data_bits=8,
    stop_bits=1,
    parity="none"
)