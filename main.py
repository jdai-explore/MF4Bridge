#!/usr/bin/env python3
"""
MF4Bridge - MDF4 File Converter
Main application entry point with simplified, robust startup logic
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_python_version():
    """Ensure minimum Python version requirement"""
    if sys.version_info < (3, 8):
        error_msg = f"Python 3.8+ required. Current version: {sys.version}"
        logger.error(error_msg)
        try:
            messagebox.showerror("Python Version Error", error_msg)
        except:
            print(error_msg)
        return False
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    optional_deps = []
    
    # Check for asammdf (core functionality)
    try:
        import asammdf
        logger.info(f"✓ asammdf {asammdf.__version__} found")
    except ImportError:
        logger.warning("✗ asammdf not found - will run in demo mode")
        missing_deps.append('asammdf')
    
    # Check for CustomTkinter (optional, for better UI)
    try:
        import customtkinter
        logger.info(f"✓ customtkinter found")
    except ImportError:
        logger.info("ℹ customtkinter not found - using standard tkinter")
        optional_deps.append('customtkinter')
    
    return missing_deps, optional_deps

def create_gui():
    """Create and return the appropriate GUI instance"""
    try:
        # Try CustomTkinter first if available
        try:
            import customtkinter as ctk
            from gui_components import MF4BridgeGUI
            
            # Set appearance mode
            ctk.set_appearance_mode("system")
            ctk.set_default_color_theme("blue")
            
            root = ctk.CTk()
            logger.info("Using CustomTkinter interface")
            
        except ImportError:
            # Fall back to standard tkinter
            from gui_components import MF4BridgeGUI
            root = tk.Tk()
            logger.info("Using standard Tkinter interface")
        
        # Initialize the application
        app = MF4BridgeGUI(root)
        return root, app
        
    except Exception as e:
        logger.error(f"Failed to create GUI: {e}")
        raise

def show_dependency_info(missing_deps, optional_deps):
    """Show information about missing dependencies"""
    if not missing_deps:
        return
    
    def show_info():
        message_parts = ["MF4Bridge is running in demo mode.\n"]
        
        if missing_deps:
            message_parts.append("Missing core dependencies:")
            for dep in missing_deps:
                message_parts.append(f"  • {dep}")
            message_parts.append("")
        
        message_parts.extend([
            "Demo mode features:",
            "  ✅ Test all functionality with sample data",
            "  ✅ Learn the interface and workflow", 
            "  ⚠️ Real MDF4 files won't be processed",
            "",
            "To enable full functionality:",
            "  pip install asammdf>=7.0.0",
            "",
            "Would you like to continue in demo mode?"
        ])
        
        result = messagebox.askyesno(
            "Demo Mode", 
            "\n".join(message_parts)
        )
        
        if not result:
            logger.info("User chose to exit and install dependencies")
            sys.exit(0)
    
    return show_info

def main():
    """Main application entry point"""
    logger.info("Starting MF4Bridge...")
    
    try:
        # Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Check dependencies
        missing_deps, optional_deps = check_dependencies()
        
        # Create GUI
        root, app = create_gui()
        
        # Show dependency info if needed (after GUI loads)
        if missing_deps:
            demo_info_func = show_dependency_info(missing_deps, optional_deps)
            root.after(1000, demo_info_func)  # Show after 1 second
        
        logger.info("MF4Bridge started successfully")
        
        # Start the main event loop
        root.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        error_msg = f"Failed to start MF4Bridge: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        try:
            messagebox.showerror("Startup Error", error_msg)
        except:
            print(error_msg)
        
        sys.exit(1)

if __name__ == "__main__":
    main()