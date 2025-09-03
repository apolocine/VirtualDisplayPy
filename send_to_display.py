#!/usr/bin/env python3
"""
📤 Send to Display - Message sender for GUI communication
Date: 03/09/2025
Description: Send messages to running VirtualDisplayPy GUI via file communication
"""

import sys
import time
import tempfile
import os
from datetime import datetime

def send_message_to_display(port_name: str, message: str):
    """Send message to specific display port"""
    message_file = os.path.join(tempfile.gettempdir(), "virtualdisplay_messages.txt")
    
    # Prepare message in format: PORT|MESSAGE
    formatted_message = f"{port_name}|{message}\n"
    
    # Append to message file
    with open(message_file, 'a', encoding='utf-8') as f:
        f.write(formatted_message)
    
    print(f"📤 Message envoyé vers {port_name}: '{message}'")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("📡 Send to Display - Envoyer messages vers VirtualDisplayPy GUI")
        print("=" * 60)
        print()
        print("Usage:")
        print(f"  {sys.argv[0]} <message>")
        print(f"  {sys.argv[0]} <port_name> <message>")
        print()
        print("Exemples:")
        print(f"  {sys.argv[0]} 'Hello World!'")
        print(f"  {sys.argv[0]} COM_SERIAL 'Message spécifique'")
        print(f"  {sys.argv[0]} USB_DISPLAY 'Test USB'")
        print()
        print("Ports communs: COM_SERIAL, USB_DISPLAY, USB_SERIAL")
        print()
        print("💡 Astuce: Lancez './run.sh gui' d'abord, créez des afficheurs,")
        print("          puis utilisez ce script pour envoyer des messages!")
        return
    
    # Parse arguments
    if len(sys.argv) == 2:
        # Send to all common ports
        message = sys.argv[1]
        ports = ["COM_SERIAL", "USB_DISPLAY", "USB_SERIAL"]
        
        print("📡 Envoi de messages vers VirtualDisplayPy GUI")
        print("=" * 50)
        print(f"📝 Message: '{message}'")
        print(f"🎯 Ports cibles: {', '.join(ports)}")
        print()
        
        for port in ports:
            send_message_to_display(port, message)
        
        print()
        print("🎉 Messages envoyés!")
        
    elif len(sys.argv) == 3:
        # Send to specific port
        port_name = sys.argv[1]
        message = sys.argv[2]
        
        print("📡 Envoi de message vers VirtualDisplayPy GUI")
        print("=" * 50)
        print(f"📝 Message: '{message}'")
        print(f"🎯 Port cible: {port_name}")
        print()
        
        send_message_to_display(port_name, message)
        
        print()
        print("🎉 Message envoyé!")
    
    print()
    print("👀 Vérifiez l'interface graphique VirtualDisplayPy")
    print("   Le message devrait apparaître dans la section 'Contenu des Afficheurs'")
    print("   et être visible dans le 'Journal d'Activité'")

if __name__ == "__main__":
    main()