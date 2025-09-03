#!/usr/bin/env python3
"""
📡 Test External Messages - Simple test script
Date: 03/09/2025
Description: Simple test script to demonstrate external message sending
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.serial_emulator import SerialEmulator
from models.display_config import VirtualDisplayConfig, ConnectionType

async def test_external_messages():
    """Test sending messages from external application"""
    print("🔄 Testing external message sending...")
    print()
    
    # Create a separate emulator instance (simulating external app)
    external_emulator = SerialEmulator()
    
    # Test messages to send
    test_messages = [
        "External App Test 1",
        "Hello VirtualDisplay!",
        f"Time: {time.strftime('%H:%M:%S')}",
        "Message from external",
        "Test completed!"
    ]
    
    # Common port names that might exist
    test_ports = ["COM_SERIAL", "USB_DISPLAY", "USB_SERIAL"]
    
    print("🔍 Looking for existing virtual displays...")
    found_port = None
    
    for port_name in test_ports:
        if port_name in external_emulator.ports:
            found_port = port_name
            print(f"✅ Found display: {port_name}")
            break
    
    if not found_port:
        print("⚠️  No existing displays found.")
        print("   Creating a test display...")
        
        # Create a test display
        config = VirtualDisplayConfig(
            port_name="EXTERNAL_TEST",
            connection_type=ConnectionType.SERIAL,
            baud_rate=9600
        )
        
        success = await external_emulator.create_virtual_port(config)
        if success:
            await external_emulator.open_port("EXTERNAL_TEST", config)
            found_port = "EXTERNAL_TEST"
            print(f"✅ Created test display: {found_port}")
        else:
            print("❌ Failed to create test display")
            return
    
    print()
    print(f"📤 Sending {len(test_messages)} test messages to {found_port}")
    print()
    
    # Send test messages
    config = VirtualDisplayConfig(
        port_name=found_port,
        connection_type=ConnectionType.SERIAL,
        baud_rate=9600
    )
    
    for i, message in enumerate(test_messages, 1):
        try:
            print(f"[{i}/{len(test_messages)}] Sending: '{message}'")
            
            comm = await external_emulator.send_message(found_port, message, config)
            
            if comm.status.value == "success":
                print(f"    ✅ Success (latency: {comm.latency:.1f}ms)")
            else:
                print(f"    ❌ Failed: {comm.error}")
            
            if i < len(test_messages):
                await asyncio.sleep(2)  # Wait 2 seconds between messages
                
        except Exception as e:
            print(f"    💥 Error: {e}")
    
    print()
    print("🎉 External message test completed!")
    print("   If VirtualDisplayPy GUI is running, check for the messages on the displays.")

def main():
    """Main function"""
    print("=" * 60)
    print("📡 VirtualDisplayPy - External Message Test")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(test_external_messages())
    except KeyboardInterrupt:
        print("\\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()