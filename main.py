#!/usr/bin/env python3
"""
MF4Bridge - MDF4 File Converter
Main application entry point
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Check for asammdf
    try:
        import asammdf
        print("✓ asammdf found")
    except ImportError as e:
        print(f"✗ asammdf not found: {e}")
        missing_deps.append('asammdf')
    
    return missing_deps

def main():
    """Main application entry point"""
    try:
        print("MF4Bridge - Starting up...")
        
        # Check dependencies
        missing = check_dependencies()
        
        # Try to import GUI components with fallback system
        gui_imported = False
        
        # Try CustomTkinter version first
        if not missing:
            try:
                from gui_components import MF4BridgeGUI
                print("Using CustomTkinter interface with full asammdf support")
                gui_imported = True
            except ImportError as e:
                print(f"CustomTkinter version failed: {e}")
        
        # Try standard tkinter version with asammdf
        if not gui_imported and not missing:
            try:
                from gui_components import MF4BridgeGUI
                print("Using standard Tkinter interface with full asammdf support")
                gui_imported = True
            except ImportError as e:
                print(f"Standard tkinter version failed: {e}")
        
        # Fall back to minimal version without asammdf
        if not gui_imported:
            try:
                # Create minimal version dynamically
                print("⚠️  Using demo mode - asammdf not available")
                print("   This will generate sample data instead of reading real MDF4 files")
                
                # Import minimal converter
                from converter_engine import MF4Converter
                
                # Import simple GUI but patch it to use minimal converter
                from gui_components import MF4BridgeGUI as SimpleGUI
                
                # Override the converter import in the GUI module
                import gui_components
                gui_components.MF4Converter = MF4Converter
                
                MF4BridgeGUI = SimpleGUI
                gui_imported = True
                
            except ImportError as e:
                print(f"Minimal version failed: {e}")
        
        if not gui_imported:
            print("✗ Could not import any GUI version")
            print("\nTry fixing the environment:")
            print("python fix_environment.py")
            return
        
        # Create main window
        root = tk.Tk()
        
        # Initialize the application
        app = MF4BridgeGUI(root)
        
        # Show dependency info if running in demo mode
        if missing:
            # Don't show popup immediately - let user see the GUI first
            def show_demo_info():
                result = messagebox.askyesno(
                    "Demo Mode Active", 
                    "MF4Bridge is running in demo mode.\n\n"
                    "✅ You can test all functionality with sample data\n"
                    "⚠️ Real MDF4 files won't be processed\n\n"
                    "Would you like to fix this and enable real MDF4 processing?\n\n"
                    "Click 'Yes' to get installation instructions\n"
                    "Click 'No' to continue with demo mode"
                )
                
                if result:
                    messagebox.showinfo(
                        "Enable Real MDF4 Processing",
                        "To enable real MDF4 file processing:\n\n"
                        "1. Close MF4Bridge\n"
                        "2. Run: python fix_environment.py\n"
                        "3. Restart: python main.py\n\n"
                        "This will install the required asammdf library."
                    )
            
            # Show demo info after a delay to let GUI load
            root.after(1000, show_demo_info)
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Failed to start MF4Bridge: {str(e)}"
        print(error_msg)
        try:
            messagebox.showerror("Error", error_msg)
        except:
            pass  # GUI might not be available
        sys.exit(1)

if __name__ == "__main__":
    main()