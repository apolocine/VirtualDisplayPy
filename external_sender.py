#!/usr/bin/env python3
"""
🚀 External Message Sender - Test script for sending messages to VirtualDisplayPy
Date: 03/09/2025
Description: Demonstrates how to send messages from another application to the virtual displays
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.serial_emulator import SerialEmulator
from models.display_config import VirtualDisplayConfig, ConnectionType, DisplayTheme

class ExternalMessageSender:
    """External application that sends messages to virtual displays"""
    
    def __init__(self):
        self.serial_emulator = SerialEmulator()
        print("🔌 External Message Sender initialized")
        print("   This simulates another application sending messages to VirtualDisplayPy")
        print()
    
    async def connect_to_display(self, port_name: str, connection_type: ConnectionType = ConnectionType.SERIAL):
        """Connect to an existing virtual display"""
        print(f"🔍 Searching for virtual display: {port_name}")
        
        # Check if display exists in the emulator
        if port_name in self.serial_emulator.ports:
            print(f"✅ Found virtual display: {port_name}")
            return True
        else:
            print(f"❌ Virtual display not found: {port_name}")
            print("   Make sure VirtualDisplayPy GUI is running with a display created")
            return False
    
    async def send_message(self, port_name: str, message: str):
        """Send message to virtual display"""
        try:
            # Get the display configuration (simplified)
            config = VirtualDisplayConfig(
                port_name=port_name,
                connection_type=ConnectionType.SERIAL,
                baud_rate=9600
            )
            
            print(f"📤 Sending message to {port_name}: '{message}'")
            comm = await self.serial_emulator.send_message(port_name, message, config)
            
            if comm.status.value == "success":
                print(f"✅ Message sent successfully (latency: {comm.latency:.1f}ms)")
                return True
            else:
                print(f"❌ Message failed: {comm.error}")
                return False
                
        except Exception as e:
            print(f"💥 Error sending message: {e}")
            return False
    
    async def send_multiple_messages(self, port_name: str, messages: list, delay: float = 2.0):
        """Send multiple messages with delay"""
        print(f"📋 Sending {len(messages)} messages to {port_name} with {delay}s delay")
        print()
        
        for i, message in enumerate(messages, 1):
            print(f"[{i}/{len(messages)}]", end=" ")
            success = await self.send_message(port_name, message)
            
            if success and i < len(messages):
                print(f"⏱️  Waiting {delay}s before next message...")
                await asyncio.sleep(delay)
            
            print()
        
        print("🎉 All messages sent!")

async def main():
    """Main demonstration function"""
    print("=" * 60)
    print("🚀 VirtualDisplayPy - External Message Sender")
    print("=" * 60)
    print()
    
    sender = ExternalMessageSender()
    
    # Common display port names from the GUI
    display_ports = ["COM_SERIAL", "USB_DISPLAY", "USB_SERIAL"]
    
    print("🔍 Looking for active virtual displays...")
    active_ports = []
    
    for port in display_ports:
        if await sender.connect_to_display(port):
            active_ports.append(port)
    
    if not active_ports:
        print()
        print("⚠️  No virtual displays found!")
        print("   Please start VirtualDisplayPy GUI and create some displays first:")
        print("   1. Run: ./run.sh gui")
        print("   2. Click 'Créer Afficheur Série', 'Créer Afficheur USB', or 'Créer USB-Série'")
        print("   3. Run this script again")
        return
    
    print()
    print(f"✅ Found {len(active_ports)} active display(s): {', '.join(active_ports)}")
    print()
    
    # Demo messages
    demo_messages = [
        "Hello from External App!",
        "Message 2",
        f"Time: {time.strftime('%H:%M:%S')}",
        "Final message"
    ]
    
    # Send messages to first available display
    target_port = active_ports[0]
    print(f"🎯 Target display: {target_port}")
    print()
    
    await sender.send_multiple_messages(target_port, demo_messages, delay=3.0)
    
    print()
    print("🔚 External sender completed")
    print("   Check VirtualDisplayPy GUI to see the messages!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)