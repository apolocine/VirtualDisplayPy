"""
🔌 Serial Emulator - Core Communication Engine
Date: 03/09/2025
Description: Complete serial port emulation with USB and network support
"""

import asyncio
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import asdict
from queue import Queue, Empty
import logging
import random

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

from models.display_config import (
    VirtualDisplayConfig, ConnectionType, ConnectionStatus, FailureType, COMMON_COMMANDS
)
from models.communication import (
    Communication, DisplayCommand, ErrorRecord, 
    CommunicationDirection, CommunicationStatus, CommandStatus,
    USBDeviceInfo, NetworkConnection, SERIAL_PROTOCOLS, USB_PROTOCOLS
)


class SerialPortMock:
    """Mock serial port for simulation"""
    def __init__(self, port_name: str, config: VirtualDisplayConfig):
        self.port_name = port_name
        self.config = config
        self.is_open = False
        self.buffer = bytearray()
        self.last_activity = datetime.now()
        self.statistics = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'messages_processed': 0,
            'errors': 0
        }
    
    def write(self, data: bytes) -> int:
        """Simulate writing data to port"""
        if not self.is_open:
            raise Exception(f"Port {self.port_name} not open")
        
        self.statistics['bytes_sent'] += len(data)
        self.last_activity = datetime.now()
        return len(data)
    
    def read(self, size: int = 1) -> bytes:
        """Simulate reading data from port"""
        if not self.is_open:
            raise Exception(f"Port {self.port_name} not open")
        
        if len(self.buffer) >= size:
            data = bytes(self.buffer[:size])
            self.buffer = self.buffer[size:]
            self.statistics['bytes_received'] += len(data)
            return data
        return b""
    
    def close(self):
        """Close the mock port"""
        self.is_open = False
        self.buffer.clear()


class USBDisplayMock:
    """Mock USB display device"""
    def __init__(self, device_info: USBDeviceInfo):
        self.device_info = device_info
        self.is_connected = False
        self.buffer = bytearray()
        self.last_activity = datetime.now()
    
    def write(self, data: bytes, endpoint: int = None) -> int:
        """Write data to USB device"""
        if not self.is_connected:
            raise Exception("USB device not connected")
        
        endpoint = endpoint or self.device_info.endpoint_out
        # Simulate USB HID write
        self.last_activity = datetime.now()
        return len(data)
    
    def read(self, size: int, endpoint: int = None) -> bytes:
        """Read data from USB device"""
        if not self.is_connected:
            raise Exception("USB device not connected")
        
        endpoint = endpoint or self.device_info.endpoint_in
        # Simulate USB HID read
        if len(self.buffer) >= size:
            data = bytes(self.buffer[:size])
            self.buffer = self.buffer[size:]
            return data
        return b""


class USBSerialDisplayMock:
    """Mock USB-to-Serial bridge display (FTDI, CH340, etc.)"""
    def __init__(self, port_name: str, config: VirtualDisplayConfig):
        self.port_name = port_name
        self.config = config
        self.is_open = False
        self.is_connected = False  # For compatibility with send_message method
        self.buffer = bytearray()
        self.last_activity = datetime.now()
        
        # USB-Serial specific properties
        self.usb_vendor_id = config.usb_vendor_id
        self.usb_product_id = config.usb_product_id
        self.serial_number = getattr(config, 'usb_serial_number', f"USB{random.randint(100000, 999999)}")
        
        # Serial port properties
        self.baud_rate = config.baud_rate or 9600
        self.data_bits = getattr(config, 'data_bits', 8)
        self.stop_bits = getattr(config, 'stop_bits', 1)
        self.parity = getattr(config, 'parity', 'none')
        self.flow_control = getattr(config, 'flow_control', 'none')
        
        self.statistics = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'messages_count': 0,
            'connection_time': None,
            'last_message_time': None
        }
    
    def write(self, data: bytes) -> int:
        """Write data to USB-Serial bridge"""
        if not self.is_open:
            raise Exception("USB-Serial port not open")
        
        # Simulate USB-Serial conversion delay (typically faster than pure serial)
        time.sleep(random.uniform(0.001, 0.005))  # 1-5ms delay
        
        self.last_activity = datetime.now()
        self.statistics['bytes_sent'] += len(data)
        self.statistics['messages_count'] += 1
        self.statistics['last_message_time'] = datetime.now()
        
        # Add data to buffer for potential read operations
        self.buffer.extend(data)
        return len(data)
    
    async def write_data(self, data: bytes) -> int:
        """Asynchronous write method for compatibility"""
        return self.write(data)
    
    def read(self, size: int = 1) -> bytes:
        """Read data from USB-Serial bridge"""
        if not self.is_open:
            raise Exception("USB-Serial port not open")
        
        if len(self.buffer) >= size:
            data = bytes(self.buffer[:size])
            self.buffer = self.buffer[size:]
            self.statistics['bytes_received'] += len(data)
            return data
        return b""
    
    def open(self) -> bool:
        """Open USB-Serial connection"""
        self.is_open = True
        self.is_connected = True  # Set both for compatibility
        self.statistics['connection_time'] = datetime.now()
        return True
    
    def close(self):
        """Close USB-Serial connection"""
        self.is_open = False
        self.is_connected = False  # Set both for compatibility
        self.buffer.clear()
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get USB device information"""
        return {
            'vendor_id': self.usb_vendor_id,
            'product_id': self.usb_product_id,
            'serial_number': self.serial_number,
            'baud_rate': self.baud_rate,
            'data_bits': self.data_bits,
            'stop_bits': self.stop_bits,
            'parity': self.parity,
            'flow_control': self.flow_control,
            'driver': self._get_driver_name()
        }
    
    def _get_driver_name(self) -> str:
        """Get appropriate driver name based on VID/PID"""
        if self.usb_vendor_id == "0403":  # FTDI
            return "FTDI FT232R"
        elif self.usb_vendor_id == "1a86":  # CH340
            return "CH340G"
        elif self.usb_vendor_id == "067b":  # Prolific
            return "PL2303"
        elif self.usb_vendor_id == "10c4":  # Silicon Labs
            return "CP2102"
        else:
            return "Generic USB-Serial"


class NetworkDisplayMock:
    """Mock network display connection"""
    def __init__(self, connection: NetworkConnection):
        self.connection = connection
        self.socket = None
        self.last_ping = None
    
    async def connect(self) -> bool:
        """Simulate network connection"""
        # Simulate connection delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        self.connection.is_connected = True
        self.connection.connection_time = datetime.now()
        return True
    
    async def send(self, data: bytes) -> int:
        """Send data over network"""
        if not self.connection.is_connected:
            raise Exception("Network not connected")
        
        # Simulate network latency
        await asyncio.sleep(random.uniform(0.01, 0.1))
        return len(data)
    
    async def receive(self, size: int) -> bytes:
        """Receive data from network"""
        if not self.connection.is_connected:
            raise Exception("Network not connected")
        
        # Simulate empty response for now
        return b""


class SerialEmulator:
    """
    Complete serial emulation engine supporting serial, USB, and network connections
    """
    
    def __init__(self):
        self.ports: Dict[str, Union[SerialPortMock, USBDisplayMock, NetworkDisplayMock]] = {}
        self.active_connections: Dict[str, ConnectionType] = {}
        self.display_content: Dict[str, List[str]] = {}  # Store current display content
        self.message_queue: Queue = Queue()
        self.is_processing = False
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.statistics = {
            'total_messages': 0,
            'successful_messages': 0,
            'failed_messages': 0,
            'average_latency': 0.0,
            'active_connections': 0
        }
        self.logger = logging.getLogger(__name__)
        
        # Start message processor
        self._start_message_processor()
    
    def on(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def off(self, event: str, handler: Callable):
        """Unregister event handler"""
        if event in self.event_handlers and handler in self.event_handlers[event]:
            self.event_handlers[event].remove(handler)
    
    def emit(self, event: str, data: Any):
        """Emit event to all registered handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event}: {e}")
    
    async def create_virtual_port(self, config: VirtualDisplayConfig) -> bool:
        """Create a virtual port based on configuration"""
        try:
            if config.port_name in self.ports:
                raise Exception(f"Port {config.port_name} already exists")
            
            # Create appropriate port type based on connection type
            if config.connection_type == ConnectionType.SERIAL:
                port = SerialPortMock(config.port_name, config)
                
            elif config.connection_type == ConnectionType.USB:
                device_info = USBDeviceInfo(
                    vendor_id=config.usb_vendor_id or "04D8",
                    product_id=config.usb_product_id or "000A",
                    serial_number=config.usb_serial_number,
                    interface_number=config.usb_interface
                )
                port = USBDisplayMock(device_info)
                
            elif config.connection_type == ConnectionType.USB_SERIAL:
                device_info = USBDeviceInfo(
                    vendor_id=config.usb_vendor_id or "0403",  # FTDI default
                    product_id=config.usb_product_id or "6001",  # FT232R default
                    serial_number=config.usb_serial_number,
                    interface_number=config.usb_interface
                )
                port = USBSerialDisplayMock(config.port_name, config)
                
            elif config.connection_type == ConnectionType.NETWORK:
                network_conn = NetworkConnection(
                    host=config.network_host,
                    port=config.network_port,
                    protocol=config.network_protocol
                )
                port = NetworkDisplayMock(network_conn)
                
            else:
                raise Exception(f"Unsupported connection type: {config.connection_type}")
            
            self.ports[config.port_name] = port
            
            # Simulate creation delay
            await asyncio.sleep(random.uniform(0.05, 0.2))
            
            self.emit('port-created', {
                'port_name': config.port_name,
                'connection_type': config.connection_type.value,
                'timestamp': datetime.now()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating virtual port {config.port_name}: {e}")
            raise
    
    async def open_port(self, port_name: str, config: VirtualDisplayConfig) -> bool:
        """Open a virtual port connection"""
        try:
            if port_name not in self.ports:
                await self.create_virtual_port(config)
            
            port = self.ports[port_name]
            
            # Simulate connection failures if configured
            if self._should_simulate_failure(config, FailureType.DISCONNECT):
                raise Exception(f"Simulated connection failure on {port_name}")
            
            # Simulate connection latency
            await asyncio.sleep(config.artificial_latency / 1000.0)
            
            # Open connection based on type
            if isinstance(port, SerialPortMock):
                port.is_open = True
                
            elif isinstance(port, USBDisplayMock):
                port.is_connected = True
                
            elif isinstance(port, NetworkDisplayMock):
                await port.connect()
            
            self.active_connections[port_name] = config.connection_type
            self.statistics['active_connections'] += 1
            
            self.emit('port-opened', {
                'port_name': port_name,
                'connection_type': config.connection_type.value,
                'timestamp': datetime.now(),
                'success': True
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening port {port_name}: {e}")
            self.emit('port-open-failed', {
                'port_name': port_name,
                'error': str(e),
                'timestamp': datetime.now()
            })
            raise
    
    async def close_port(self, port_name: str):
        """Close a port connection"""
        try:
            if port_name not in self.ports:
                return
            
            port = self.ports[port_name]
            
            if isinstance(port, SerialPortMock):
                port.close()
            elif isinstance(port, USBDisplayMock):
                port.is_connected = False
            elif isinstance(port, NetworkDisplayMock):
                port.connection.is_connected = False
            
            if port_name in self.active_connections:
                del self.active_connections[port_name]
                self.statistics['active_connections'] -= 1
            
            self.emit('port-closed', {
                'port_name': port_name,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"Error closing port {port_name}: {e}")
    
    async def send_message(self, port_name: str, message: str, config: VirtualDisplayConfig) -> Communication:
        """Send message to a virtual display"""
        start_time = time.time()
        
        try:
            if port_name not in self.ports:
                raise Exception(f"Port {port_name} not found")
            
            port = self.ports[port_name]
            data = message.encode('utf-8')
            
            # Create communication record
            comm = Communication(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                port_name=port_name,
                direction=CommunicationDirection.OUT,
                data=message,
                raw_data=data,
                size=len(data),
                status=CommunicationStatus.SUCCESS,
                sequence_number=self.statistics['total_messages'],
                is_response=False,
                connection_type=self.active_connections.get(port_name, ConnectionType.SERIAL).value
            )
            
            # Simulate transmission errors
            if self._should_simulate_failure(config, FailureType.TIMEOUT):
                comm.status = CommunicationStatus.TIMEOUT
                raise Exception("Simulated timeout")
            
            if self._should_simulate_failure(config, FailureType.CORRUPTION):
                comm.status = CommunicationStatus.CORRUPTED
                raise Exception("Simulated data corruption")
            
            # Send data based on connection type
            if isinstance(port, SerialPortMock):
                if not port.is_open:
                    raise Exception(f"Port {port_name} not open")
                await self._send_serial_data(port, data, config)
                
            elif isinstance(port, USBDisplayMock):
                if not port.is_connected:
                    raise Exception(f"USB device {port_name} not connected")
                await self._send_usb_data(port, data, config)
                
            elif isinstance(port, USBSerialDisplayMock):
                if not port.is_connected:
                    raise Exception(f"USB-Serial device {port_name} not connected")
                await self._send_usb_serial_data(port, data, config)
                
            elif isinstance(port, NetworkDisplayMock):
                if not port.connection.is_connected:
                    raise Exception(f"Network {port_name} not connected")
                await self._send_network_data(port, data, config)
            
            # Calculate latency
            end_time = time.time()
            comm.latency = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Update statistics
            self.statistics['total_messages'] += 1
            self.statistics['successful_messages'] += 1
            self._update_average_latency(comm.latency)
            
            # Process display update
            await self._process_display_message(port_name, message, config)
            
            self.emit('message-sent', asdict(comm))
            return comm
            
        except Exception as e:
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            # Update error statistics
            self.statistics['total_messages'] += 1
            self.statistics['failed_messages'] += 1
            
            error_comm = Communication(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                port_name=port_name,
                direction=CommunicationDirection.OUT,
                data=message,
                raw_data=message.encode('utf-8'),
                size=len(message),
                status=CommunicationStatus.ERROR,
                latency=latency,
                error=str(e),
                sequence_number=self.statistics['total_messages'] - 1,
                is_response=False
            )
            
            self.emit('message-failed', {
                'communication': asdict(error_comm),
                'error': e
            })
            raise
    
    async def _send_serial_data(self, port: SerialPortMock, data: bytes, config: VirtualDisplayConfig):
        """Send data via serial protocol"""
        # Add serial protocol framing if needed
        if data == b"clear":
            data = SERIAL_PROTOCOLS["CLEAR_SCREEN"]
        
        # Simulate transmission time
        transmission_time = len(data) / (config.baud_rate / 8)  # bytes per second
        await asyncio.sleep(transmission_time)
        
        port.write(data)
    
    async def _send_usb_data(self, port: USBDisplayMock, data: bytes, config: VirtualDisplayConfig):
        """Send data via USB HID protocol"""
        # Frame data for USB HID
        if data.startswith(b"clear"):
            hid_data = USB_PROTOCOLS["HID_CLEAR"]
        else:
            hid_data = USB_PROTOCOLS["HID_WRITE"] + data[:62]  # USB HID packet limit
        
        # Simulate USB transmission
        await asyncio.sleep(0.001)  # USB is fast
        port.write(hid_data)
    
    async def _send_usb_serial_data(self, port: USBSerialDisplayMock, data: bytes, config: VirtualDisplayConfig):
        """Send data via USB-Serial bridge"""
        # Simulate USB-Serial bridge conversion delay
        await asyncio.sleep(0.002)  # 2ms for USB-Serial conversion
        
        # Apply serial framing
        if data.startswith(b"clear"):
            serial_data = COMMON_COMMANDS["CLEAR_SCREEN"].encode()
        else:
            serial_data = data + COMMON_COMMANDS["NEW_LINE"].encode()
        
        # Write data through USB-Serial bridge
        await port.write_data(serial_data)
    
    async def _send_network_data(self, port: NetworkDisplayMock, data: bytes, config: VirtualDisplayConfig):
        """Send data via network protocol"""
        # Frame data for network transmission
        network_data = data  # Could add JSON/XML framing here
        
        await port.send(network_data)
    
    async def _process_display_message(self, port_name: str, message: str, config: VirtualDisplayConfig):
        """Process message for display rendering"""
        # Handle clear command
        if message.strip() == "" or message.lower().startswith("clear"):
            lines = [""] * config.display_lines
        else:
            lines = message.split('\n')
            
            # Limit lines to display capacity
            if len(lines) > config.display_lines:
                lines = lines[:config.display_lines]
            
            # Pad with empty lines if needed
            while len(lines) < config.display_lines:
                lines.append("")
            
            # Truncate lines to display width
            for i, line in enumerate(lines):
                if len(line) > config.line_length:
                    lines[i] = line[:config.line_length]
        
        # Store the content
        self.display_content[port_name] = lines
        
        self.emit('display-update', {
            'port_name': port_name,
            'content': lines,
            'timestamp': datetime.now(),
            'config': asdict(config)
        })
        
        # Simulate acknowledgment
        await asyncio.sleep(0.01)
        ack_comm = Communication(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            port_name=port_name,
            direction=CommunicationDirection.IN,
            data="ACK",
            raw_data=b"ACK",
            size=3,
            status=CommunicationStatus.SUCCESS,
            sequence_number=self.statistics['total_messages'],
            is_response=True
        )
        
        self.emit('message-received', asdict(ack_comm))
    
    def _should_simulate_failure(self, config: VirtualDisplayConfig, failure_type: FailureType) -> bool:
        """Check if a failure should be simulated"""
        if failure_type not in config.simulated_failures:
            return False
        
        return random.random() * 100 < config.error_rate
    
    def _update_average_latency(self, latency: float):
        """Update running average latency"""
        successful_messages = self.statistics['successful_messages']
        if successful_messages == 1:
            self.statistics['average_latency'] = latency
        else:
            current_avg = self.statistics['average_latency']
            self.statistics['average_latency'] = (current_avg * (successful_messages - 1) + latency) / successful_messages
    
    def _start_message_processor(self):
        """Start background message processing"""
        def process_messages():
            self.is_processing = True
            while self.is_processing:
                try:
                    # Process queued commands
                    if not self.message_queue.empty():
                        command = self.message_queue.get_nowait()
                        asyncio.run(self._execute_command(command))
                    
                    time.sleep(0.05)  # 50ms polling
                except Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing messages: {e}")
        
        threading.Thread(target=process_messages, daemon=True).start()
    
    async def _execute_command(self, command: DisplayCommand):
        """Execute a display command"""
        try:
            command.status = CommandStatus.EXECUTING
            command.executed_at = datetime.now()
            
            if command.type.value == "clear":
                self.emit('display-clear', {'port_name': command.port_name})
            elif command.type.value == "write":
                await self.send_message(command.port_name, str(command.data), None)
            
            command.status = CommandStatus.COMPLETED
            command.completed_at = datetime.now()
            
            self.emit('command-completed', asdict(command))
            
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error = str(e)
            command.completed_at = datetime.now()
            
            self.emit('command-failed', asdict(command))
    
    def queue_command(self, command_data: Dict[str, Any]) -> str:
        """Queue a command for execution"""
        command = DisplayCommand(
            id=str(uuid.uuid4()),
            **command_data,
            timestamp=datetime.now()
        )
        
        self.message_queue.put(command)
        self.emit('command-queued', asdict(command))
        return command.id
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get emulator statistics"""
        return {
            **self.statistics,
            'available_ports': len(self.ports),
            'queue_length': self.message_queue.qsize()
        }
    
    def get_port_status(self, port_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific port"""
        if port_name not in self.ports:
            return None
        
        port = self.ports[port_name]
        
        if isinstance(port, SerialPortMock):
            return {
                'type': 'serial',
                'is_open': port.is_open,
                'statistics': port.statistics,
                'last_activity': port.last_activity
            }
        elif isinstance(port, USBDisplayMock):
            return {
                'type': 'usb',
                'is_connected': port.is_connected,
                'device_info': asdict(port.device_info),
                'last_activity': port.last_activity
            }
        elif isinstance(port, NetworkDisplayMock):
            return {
                'type': 'network',
                'is_connected': port.connection.is_connected,
                'connection': asdict(port.connection),
                'last_ping': port.last_ping
            }
    
    def list_ports(self) -> List[str]:
        """List all available port names"""
        return list(self.ports.keys())
    
    async def reset_port(self, port_name: str, config: VirtualDisplayConfig):
        """Reset a port connection"""
        await self.close_port(port_name)
        await asyncio.sleep(0.1)
        await self.open_port(port_name, config)
    
    def destroy(self):
        """Clean shutdown of the emulator"""
        self.is_processing = False
        
        # Close all connections
        for port_name in list(self.active_connections.keys()):
            asyncio.run(self.close_port(port_name))
        
        self.ports.clear()
        self.active_connections.clear()
        
        # Clear queues
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except Empty:
                break
        
        self.event_handlers.clear()
        self.display_content.clear()
        self.logger.info("Serial emulator destroyed")
    
    def get_display_content(self, port_name: str) -> List[str]:
        """Get current display content for a port"""
        return self.display_content.get(port_name, [])