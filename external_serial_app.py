#!/usr/bin/env python3
"""
📡 External Serial Application - Real pyserial communication
Date: 03/09/2025
Description: Example of how a real external application would communicate with VirtualDisplayPy
using standard pyserial library (not the internal emulator API)
"""

import time
import sys
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("❌ pyserial not available. Install with: pip install pyserial")
    sys.exit(1)

class ExternalSerialApp:
    """External application using standard pyserial to communicate"""
    
    def __init__(self):
        self.connections = {}
        print("📡 External Serial Application initialized")
        print("   This demonstrates real serial communication with VirtualDisplayPy")
        print()
    
    def list_available_ports(self):
        """List available serial ports"""
        print("🔍 Scanning for available serial ports...")
        ports = serial.tools.list_ports.comports()
        
        if not ports:
            print("❌ No serial ports found")
            return []
        
        available_ports = []
        for port in ports:
            print(f"📍 Found port: {port.device}")
            print(f"   Description: {port.description}")
            print(f"   Hardware ID: {port.hwid}")
            available_ports.append(port.device)
        
        return available_ports
    
    def connect_to_port(self, port_name: str, baud_rate: int = 9600, timeout: float = 1.0):
        """Connect to a serial port"""
        try:
            print(f"🔌 Connecting to {port_name} at {baud_rate} baud...")
            
            ser = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout
            )
            
            if ser.is_open:
                self.connections[port_name] = ser
                print(f"✅ Connected to {port_name}")
                return True
            else:
                print(f"❌ Failed to open {port_name}")
                return False
                
        except serial.SerialException as e:
            print(f"❌ Serial error: {e}")
            return False
        except Exception as e:
            print(f"💥 Error: {e}")
            return False
    
    def send_message(self, port_name: str, message: str):
        """Send message to connected port"""
        if port_name not in self.connections:
            print(f"❌ Not connected to {port_name}")
            return False
        
        try:
            ser = self.connections[port_name]
            
            # Add newline if not present
            if not message.endswith('\\n') and not message.endswith('\\r\\n'):
                message += '\\r\\n'
            
            # Send message
            bytes_sent = ser.write(message.encode('utf-8'))
            ser.flush()  # Ensure data is sent immediately
            
            print(f"📤 Sent {bytes_sent} bytes to {port_name}: '{message.strip()}'")
            
            # Try to read response (if any)
            time.sleep(0.1)  # Give time for response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                print(f"📥 Response: '{response.strip()}'")
            
            return True
            
        except Exception as e:
            print(f"💥 Error sending message: {e}")
            return False
    
    def send_multiple_messages(self, port_name: str, messages: list, delay: float = 2.0):
        """Send multiple messages with delay"""
        print(f"📋 Sending {len(messages)} messages to {port_name}")
        print()
        
        success_count = 0
        for i, message in enumerate(messages, 1):
            print(f"[{i}/{len(messages)}]", end=" ")
            
            if self.send_message(port_name, message):
                success_count += 1
            
            if i < len(messages):
                print(f"⏱️  Waiting {delay}s...")
                time.sleep(delay)
            
            print()
        
        print(f"📊 Results: {success_count}/{len(messages)} messages sent successfully")
        return success_count
    
    def disconnect_all(self):
        """Disconnect from all ports"""
        for port_name, ser in self.connections.items():
            try:
                ser.close()
                print(f"🔚 Disconnected from {port_name}")
            except Exception as e:
                print(f"⚠️  Error disconnecting from {port_name}: {e}")
        
        self.connections.clear()

def main():
    """Main demonstration"""
    print("=" * 60)
    print("📡 VirtualDisplayPy - External Serial Application Demo")
    print("=" * 60)
    print()
    
    app = ExternalSerialApp()
    
    # List available ports
    ports = app.list_available_ports()
    
    if not ports:
        print()
        print("⚠️  No serial ports found!")
        print("   VirtualDisplayPy creates virtual serial ports that appear as real ports.")
        print("   Make sure VirtualDisplayPy is running with displays created.")
        print()
        print("   Steps to test:")
        print("   1. Run: ./run.sh gui")
        print("   2. Create some virtual displays")
        print("   3. Run this script again")
        return
    
    # Try to connect to the first available port
    target_port = ports[0]
    if not app.connect_to_port(target_port):
        print("❌ Failed to connect to any port")
        return
    
    print()
    
    # Demo messages
    demo_messages = [
        f"Hello from External App at {datetime.now().strftime('%H:%M:%S')}",
        "This is message #2",
        "Testing VirtualDisplayPy",
        "Display update test",
        f"Final message at {datetime.now().strftime('%H:%M:%S')}"
    ]
    
    # Send messages
    print(f"🎯 Target port: {target_port}")
    success_count = app.send_multiple_messages(target_port, demo_messages, delay=2.5)
    
    print()
    if success_count > 0:
        print("🎉 Messages sent successfully!")
        print("   Check VirtualDisplayPy GUI to see the messages on the display!")
    else:
        print("❌ No messages were sent successfully")
    
    # Cleanup
    app.disconnect_all()
    print()
    print("🔚 External serial application completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()