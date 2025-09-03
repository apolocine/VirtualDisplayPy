#!/usr/bin/env python3
"""
🖥️ VirtualDisplayPy - Simple Launcher (without GUI)
Date: 03/09/2025
Description: Simple launcher to test the core functionality without Qt issues
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.serial_emulator import SerialEmulator
from core.display_renderer import DisplayRenderer
from models.display_config import VirtualDisplayConfig, ConnectionType, DisplayTheme

def create_test_config() -> VirtualDisplayConfig:
    """Create a test display configuration"""
    return VirtualDisplayConfig(
        port_name="COM_TEST",
        connection_type=ConnectionType.SERIAL,
        baud_rate=9600,
        display_lines=2,
        line_length=20,
        theme=DisplayTheme.LCD_GREEN,
        font_size=12,
        brightness=100,
        contrast=80,
        clear_on_connect=True,
        cursor_visible=False,
        blinking_cursor=False
    )

async def test_emulator():
    """Test the serial emulator functionality"""
    print("🖥️ VirtualDisplayPy - Test du Noyau d'Émulation")
    print("=" * 50)
    
    # Initialize components
    emulator = SerialEmulator()
    renderer = DisplayRenderer()
    config = create_test_config()
    
    print(f"✅ Composants initialisés")
    
    try:
        # Create virtual port
        print(f"📟 Création du port virtuel {config.port_name}...")
        success = await emulator.create_virtual_port(config)
        if success:
            print(f"✅ Port {config.port_name} créé avec succès")
        else:
            print(f"❌ Échec de création du port {config.port_name}")
            return
        
        # Open port
        print(f"🔌 Ouverture du port {config.port_name}...")
        success = await emulator.open_port(config.port_name, config)
        if success:
            print(f"✅ Port {config.port_name} ouvert")
        else:
            print(f"❌ Échec d'ouverture du port {config.port_name}")
            return
        
        # Send test messages
        test_messages = [
            "Hello World!",
            "VirtualDisplayPy\nTest Message",
            "USB Display OK",
            "MostaGare v2.1\nPret pour test"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"📤 Envoi du message #{i}: {message.replace(chr(10), ' | ')}")
            success = await emulator.send_message(config.port_name, message, config)
            if success:
                print(f"✅ Message #{i} envoyé avec succès")
            else:
                print(f"❌ Échec d'envoi du message #{i}")
            
            # Short delay between messages
            await asyncio.sleep(0.5)
        
        # Get statistics
        print("\n📊 Statistiques de l'émulateur:")
        stats = emulator.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Get display state
        display = emulator.get_display_state(config.port_name)
        if display:
            print(f"\n🖥️ État de l'afficheur {config.port_name}:")
            print(f"  Actif: {'Oui' if display.is_active else 'Non'}")
            print(f"  Lignes: {len(display.current_content)}")
            print(f"  Contenu actuel:")
            for i, line in enumerate(display.current_content):
                print(f"    Ligne {i+1}: '{line}'")
        
        # Close port
        print(f"\n🔌 Fermeture du port {config.port_name}...")
        await emulator.close_port(config.port_name)
        print(f"✅ Port {config.port_name} fermé")
        
        print("\n🎉 Test terminé avec succès!")
        
    except Exception as e:
        print(f"💥 Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        emulator.destroy()
        renderer.clear_cache()

def main():
    """Main entry point"""
    print("🚀 Lancement du test VirtualDisplayPy...")
    
    try:
        asyncio.run(test_emulator())
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu par l'utilisateur")
        return 0
    except Exception as e:
        print(f"💥 Erreur fatale: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())