"""
🖥️ Communication Models
Date: 03/09/2025
Description: Communication and protocol models for virtual displays
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime
from enum import Enum


class CommunicationDirection(Enum):
    """Direction of communication"""
    IN = "in"
    OUT = "out"


class CommunicationStatus(Enum):
    """Status of communication"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CORRUPTED = "corrupted"


class CommandType(Enum):
    """Types of display commands"""
    CLEAR = "clear"
    WRITE = "write"
    CURSOR = "cursor"
    CONTROL = "control"
    CONFIG = "config"


class CommandStatus(Enum):
    """Status of command execution"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TextFormatting:
    """Text formatting options"""
    bold: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    inverse: bool = False
    alignment: Literal["left", "center", "right"] = "left"


@dataclass
class Communication:
    """Serial communication record"""
    id: str
    timestamp: datetime
    port_name: str
    direction: CommunicationDirection
    
    # Data
    data: str
    raw_data: bytes
    size: int
    
    # Metadata
    status: CommunicationStatus
    latency: Optional[float] = None
    error: Optional[str] = None
    
    # Context
    command_id: Optional[str] = None
    sequence_number: int = 0
    is_response: bool = False
    
    # Connection info
    connection_type: str = "serial"
    connection_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DisplayCommand:
    """Display command structure"""
    id: str
    type: CommandType
    data: Union[str, bytes]
    port_name: str
    timestamp: datetime
    
    # Command parameters
    line: Optional[int] = None
    column: Optional[int] = None
    formatting: Optional[TextFormatting] = None
    
    # Execution state
    status: CommandStatus = CommandStatus.PENDING
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Any] = None
    
    # USB/Network specific
    usb_endpoint: Optional[int] = None
    network_address: Optional[str] = None


@dataclass
class ErrorRecord:
    """Error record for troubleshooting"""
    id: str
    timestamp: datetime
    port_name: str
    error_type: str
    message: str
    details: Dict[str, Any]
    
    # Context
    command_id: Optional[str] = None
    recoverable: bool = True
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    # Connection specific
    connection_type: str = "serial"
    connection_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentData:
    """Payment data for MostaGare displays"""
    destination: str
    total: float
    quantity: int = 1
    price: float = 0.0
    tax: float = 0.0
    currency: str = "€"
    
    # Additional fields
    ticket_id: Optional[str] = None
    passenger_name: Optional[str] = None
    travel_date: Optional[datetime] = None
    seat_number: Optional[str] = None


@dataclass
class USBDeviceInfo:
    """USB device information"""
    vendor_id: str
    product_id: str
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    interface_number: int = 0
    endpoint_in: int = 0x81
    endpoint_out: int = 0x01
    
    # Device capabilities
    max_packet_size: int = 64
    supports_bulk_transfer: bool = True
    supports_interrupt_transfer: bool = False


@dataclass
class NetworkConnection:
    """Network connection information"""
    host: str
    port: int
    protocol: Literal["tcp", "udp"] = "tcp"
    timeout: int = 5000
    
    # Connection state
    is_connected: bool = False
    last_ping: Optional[datetime] = None
    connection_time: Optional[datetime] = None
    
    # Security (if needed)
    use_ssl: bool = False
    certificate_path: Optional[str] = None


# Protocol constants for different connection types
SERIAL_PROTOCOLS = {
    "CLEAR_SCREEN": b"\x0C",
    "CARRIAGE_RETURN": b"\r",
    "LINE_FEED": b"\n",
    "NEW_LINE": b"\r\n",
    "HOME": b"\x1B[H",
    "BACKSPACE": b"\x08",
    "TAB": b"\x09",
    "ESCAPE": b"\x1B"
}

USB_PROTOCOLS = {
    "HID_CLEAR": b"\x01\x0C",
    "HID_WRITE": b"\x02",
    "HID_CURSOR": b"\x03",
    "HID_CONFIG": b"\x04"
}

NETWORK_PROTOCOLS = {
    "JSON_COMMAND": "json",
    "BINARY_COMMAND": "binary",
    "TEXT_COMMAND": "text"
}

# MostaGare specific message templates
MOSTAGARE_TEMPLATES = {
    "PAYMENT_1L": "{destination} - {total}{currency}",
    "PAYMENT_2L": [
        "{destination}",
        "{total}{currency} - {quantity}x"
    ],
    "PAYMENT_3L": [
        "{destination}",
        "{quantity}x {price}{currency}",
        "Total: {total}{currency}"
    ],
    "PAYMENT_DETAILED": [
        "{destination} - {travel_date}",
        "{passenger_name}",
        "{quantity}x {price}{currency} + {tax}{currency}",
        "Total: {total}{currency}"
    ]
}