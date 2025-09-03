#!/usr/bin/env python3
"""
📡 Send Message to GUI - Direct message sender
Date: 03/09/2025
Description: Simple script to send a message that will be visible in the GUI
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

async def send_message_to_gui():
    """Send a test message to the GUI displays"""
    print("📡 Envoi de message vers l'interface graphique VirtualDisplayPy")
    print("=" * 60)
    
    # Create emulator instance that will share the same message system
    emulator = SerialEmulator()
    
    # Common display port names from the GUI
    test_ports = ["COM_SERIAL", "USB_DISPLAY", "USB_SERIAL"]
    
    # Test message
    test_message = f"Message externe {time.strftime('%H:%M:%S')}"
    
    print(f"🔍 Recherche d'afficheurs actifs...")
    print(f"📝 Message à envoyer: '{test_message}'")
    print()
    
    found_displays = False
    
    for port_name in test_ports:
        try:
            # Try to create the port first (in case it doesn't exist)
            config = VirtualDisplayConfig(
                port_name=port_name,
                connection_type=ConnectionType.SERIAL,
                baud_rate=9600
            )
            
            # Check if port exists in the emulator
            if port_name not in emulator.ports:
                print(f"⚙️  Création du port {port_name}...")
                success = await emulator.create_virtual_port(config)
                if success:
                    await emulator.open_port(port_name, config)
                    print(f"✅ Port {port_name} créé et ouvert")
                else:
                    print(f"❌ Échec création {port_name}")
                    continue
            
            # Send the message
            print(f"📤 Envoi vers {port_name}...")
            comm = await emulator.send_message(port_name, test_message, config)
            
            if comm.status.value == "success":
                print(f"✅ Message envoyé avec succès (latence: {comm.latency:.1f}ms)")
                found_displays = True
                
                # Show current display content
                content = emulator.get_display_content(port_name)
                if content:
                    print(f"📟 Contenu affiché sur {port_name}:")
                    for i, line in enumerate(content):
                        if line.strip():
                            print(f"   Ligne {i+1}: '{line}'")
                    print()
            else:
                print(f"❌ Échec: {comm.error}")
                
        except Exception as e:
            print(f"💥 Erreur avec {port_name}: {e}")
    
    if found_displays:
        print("🎉 Message(s) envoyé(s) avec succès!")
        print("   Vérifiez l'interface graphique VirtualDisplayPy")
        print("   Le message devrait apparaître dans la section 'Contenu des Afficheurs'")
    else:
        print("⚠️  Aucun afficheur trouvé ou créé")
        print("   Assurez-vous que VirtualDisplayPy GUI est ouvert")
        print("   Ou créez des afficheurs dans l'interface graphique d'abord")
    
    print()
    print("💡 Astuce: Lancez './run.sh gui' dans un autre terminal")
    print("          Puis créez des afficheurs et relancez ce script")

def main():
    """Main function"""
    try:
        asyncio.run(send_message_to_gui())
    except KeyboardInterrupt:
        print("\\n⚠️  Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\\n💥 Erreur: {e}")

if __name__ == "__main__":
    main()