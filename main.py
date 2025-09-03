#!/usr/bin/env python3
"""
🖥️ VirtualDisplayPy - Main Application Entry Point
Date: 03/09/2025
Description: Virtual Display Emulator for MostaGare with Qt interface
"""

import sys
import os
import logging
import argparse
import asyncio
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QIcon
    QT_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        from PyQt6.QtGui import QIcon
        QT_AVAILABLE = True
    except ImportError:
        QT_AVAILABLE = False

from core.serial_emulator import SerialEmulator
from core.display_renderer import DisplayRenderer


class VirtualDisplayApp:
    """Main application controller"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.setup_logging()
        
        # Core components
        self.serial_emulator: Optional[SerialEmulator] = None
        self.display_renderer: Optional[DisplayRenderer] = None
        self.qt_app: Optional[QApplication] = None
        
        # Configuration
        self.config_dir = project_root / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("VirtualDisplayPy initializing...")
    
    def setup_logging(self):
        """Configure logging system"""
        log_level = logging.DEBUG if self.debug else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(project_root / "virtualdisplay.log")
            ]
        )
        
        # Reduce noise from some libraries
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    def initialize_core_components(self):
        """Initialize core emulation components"""
        try:
            self.logger.info("Initializing serial emulator...")
            self.serial_emulator = SerialEmulator()
            
            self.logger.info("Initializing display renderer...")
            self.display_renderer = DisplayRenderer()
            
            self.logger.info("Core components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize core components: {e}")
            return False
    
    def run_gui(self) -> int:
        """Run the Qt GUI application"""
        if not QT_AVAILABLE:
            self.logger.error("Qt not available. Please install PySide6 or PyQt6")
            return 1
        
        try:
            # Create Qt application
            self.qt_app = QApplication(sys.argv)
            self.qt_app.setApplicationName("VirtualDisplayPy")
            self.qt_app.setApplicationVersion("1.0.0")
            self.qt_app.setOrganizationName("MostaGare")
            
            # Set application icon if available
            icon_path = project_root / "resources" / "icons" / "app_icon.png"
            if icon_path.exists():
                self.qt_app.setWindowIcon(QIcon(str(icon_path)))
            
            # Initialize core components
            if not self.initialize_core_components():
                return 1
            
            # Import and create main window (after Qt app is created)
            from gui.main_window import VirtualDisplayMainWindow
            
            self.main_window = VirtualDisplayMainWindow(
                serial_emulator=self.serial_emulator,
                display_renderer=self.display_renderer
            )
            
            # Show main window
            self.main_window.show()
            
            # Setup cleanup on exit
            self.qt_app.aboutToQuit.connect(self.cleanup)
            
            self.logger.info("GUI application started")
            return self.qt_app.exec()
            
        except Exception as e:
            self.logger.error(f"Error running GUI application: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    def run_console(self) -> int:
        """Run in console mode for testing/scripting"""
        try:
            self.logger.info("Starting console mode...")
            
            # Initialize core components
            if not self.initialize_core_components():
                return 1
            
            # Import console interface
            from console_interface import ConsoleInterface
            
            console = ConsoleInterface(
                serial_emulator=self.serial_emulator,
                display_renderer=self.display_renderer
            )
            
            return console.run()
            
        except Exception as e:
            self.logger.error(f"Error in console mode: {e}")
            return 1
    
    def run_tests(self) -> int:
        """Run automated tests"""
        try:
            self.logger.info("Running automated tests...")
            
            # Initialize core components
            if not self.initialize_core_components():
                return 1
            
            from tests.automated_tests import AutomatedTestRunner
            
            test_runner = AutomatedTestRunner(
                serial_emulator=self.serial_emulator,
                display_renderer=self.display_renderer
            )
            
            success = asyncio.run(test_runner.run_all_tests())
            return 0 if success else 1
            
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            return 1
    
    def cleanup(self):
        """Clean shutdown of application"""
        self.logger.info("Cleaning up application...")
        
        try:
            if self.serial_emulator:
                self.serial_emulator.destroy()
            
            if self.display_renderer:
                self.display_renderer.clear_cache()
                
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def create_console_interface():
    """Create a simple console interface for testing without Qt"""
    import cmd
    import json
    from models.display_config import DEFAULT_DISPLAY_CONFIG, DEFAULT_USB_CONFIG
    
    class VirtualDisplayConsole(cmd.Cmd):
        intro = "VirtualDisplay Console Interface. Type help or ? to list commands."
        prompt = "(virtualdisplay) "
        
        def __init__(self):
            super().__init__()
            self.app = VirtualDisplayApp(debug=True)
            self.app.initialize_core_components()
            self.displays = {}
        
        def do_create_serial(self, line):
            """Create a serial display: create_serial COM1"""
            port_name = line.strip() or "COM1"
            config = DEFAULT_DISPLAY_CONFIG
            config.port_name = port_name
            
            try:
                result = asyncio.run(self.app.serial_emulator.create_virtual_port(config))
                if result:
                    self.displays[port_name] = config
                    print(f"✅ Serial display {port_name} created")
                else:
                    print(f"❌ Failed to create serial display {port_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        def do_create_usb(self, line):
            """Create a USB display: create_usb USB1"""
            port_name = line.strip() or "USB1"
            config = DEFAULT_USB_CONFIG
            config.port_name = port_name
            
            try:
                result = asyncio.run(self.app.serial_emulator.create_virtual_port(config))
                if result:
                    self.displays[port_name] = config
                    print(f"✅ USB display {port_name} created")
                else:
                    print(f"❌ Failed to create USB display {port_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        def do_open(self, line):
            """Open a display connection: open COM1"""
            port_name = line.strip()
            if not port_name:
                print("❌ Port name required")
                return
            
            if port_name not in self.displays:
                print(f"❌ Display {port_name} not found. Create it first.")
                return
            
            try:
                config = self.displays[port_name]
                result = asyncio.run(self.app.serial_emulator.open_port(port_name, config))
                if result:
                    print(f"✅ Display {port_name} opened")
                else:
                    print(f"❌ Failed to open display {port_name}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        def do_send(self, line):
            """Send message to display: send COM1 Hello World"""
            parts = line.split(' ', 1)
            if len(parts) < 2:
                print("❌ Usage: send <port> <message>")
                return
            
            port_name, message = parts
            if port_name not in self.displays:
                print(f"❌ Display {port_name} not found")
                return
            
            try:
                config = self.displays[port_name]
                result = asyncio.run(self.app.serial_emulator.send_message(port_name, message, config))
                print(f"✅ Message sent to {port_name}: {message}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        def do_list(self, line):
            """List all displays"""
            if not self.displays:
                print("No displays created")
                return
            
            print("\n📺 Virtual Displays:")
            for port_name, config in self.displays.items():
                status = self.app.serial_emulator.get_port_status(port_name)
                status_str = "🟢 Connected" if status and status.get('is_open', False) else "🔴 Disconnected"
                print(f"  {port_name} ({config.connection_type.value}) - {status_str}")
            print()
        
        def do_stats(self, line):
            """Show emulator statistics"""
            stats = self.app.serial_emulator.get_statistics()
            print("\n📊 Emulator Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print()
        
        def do_quit(self, line):
            """Exit the application"""
            print("👋 Goodbye!")
            self.app.cleanup()
            return True
        
        def do_exit(self, line):
            """Exit the application"""
            return self.do_quit(line)
    
    return VirtualDisplayConsole()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="VirtualDisplayPy - Virtual Display Emulator for MostaGare",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run GUI application
  python main.py --console          # Run console interface
  python main.py --test             # Run automated tests
  python main.py --debug            # Run with debug logging
        """
    )
    
    parser.add_argument('--console', action='store_true', 
                       help='Run in console mode instead of GUI')
    parser.add_argument('--test', action='store_true',
                       help='Run automated tests')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--version', action='version', version='VirtualDisplayPy 1.0.0')
    
    args = parser.parse_args()
    
    # Create application instance
    app = VirtualDisplayApp(debug=args.debug)
    
    try:
        if args.test:
            return app.run_tests()
        elif args.console or not QT_AVAILABLE:
            if not QT_AVAILABLE:
                print("⚠️  Qt not available, falling back to console mode")
                print("   Install PySide6 with: pip install PySide6")
                print()
            
            # Create simple console interface
            console = create_console_interface()
            console.cmdloop()
            return 0
        else:
            return app.run_gui()
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        app.cleanup()
        return 0
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())