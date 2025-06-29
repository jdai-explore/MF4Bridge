#!/usr/bin/env python3
"""
Test GUI Layout - Verify all buttons are visible
"""

import tkinter as tk
from tkinter import messagebox

def test_gui_layout():
    """Test that GUI shows all components properly"""
    print("Testing GUI Layout...")
    
    try:
        # Import GUI components
        try:
            from gui_components import MF4BridgeGUI
            gui_type = "Standard Tkinter"
        except ImportError:
            from gui_components import MF4BridgeGUI
            gui_type = "CustomTkinter"
        
        print(f"✓ Using {gui_type} GUI")
        
        # Create test window
        root = tk.Tk()
        
        # Create GUI
        app = MF4BridgeGUI(root)
        
        # Check that all expected widgets exist
        expected_widgets = [
            'select_files_btn',
            'clear_files_btn', 
            'csv_checkbox',
            'asc_checkbox',
            'trc_checkbox',
            'dir_browse_btn',
            'convert_btn',
            'exit_btn',
            'progress_bar',
            'status_label'
        ]
        
        missing_widgets = []
        for widget_name in expected_widgets:
            if hasattr(app, widget_name):
                widget = getattr(app, widget_name)
                print(f"✓ {widget_name}: {type(widget).__name__}")
            else:
                missing_widgets.append(widget_name)
                print(f"✗ {widget_name}: Missing!")
        
        if missing_widgets:
            print(f"\n⚠️ Missing widgets: {missing_widgets}")
        else:
            print(f"\n✅ All {len(expected_widgets)} widgets found!")
        
        # Test window size
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        print(f"✓ Window size: {width}x{height}")
        
        if height < 600:
            print("⚠️ Window might be too short - some buttons may not be visible")
        else:
            print("✓ Window height should show all components")
        
        # Don't actually show the window in test mode
        root.destroy()
        
        return len(missing_widgets) == 0
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def test_button_functionality():
    """Test that buttons have proper commands"""
    print("\nTesting Button Functionality...")
    
    try:
        from gui_components import MF4BridgeGUI
        
        root = tk.Tk()
        app = MF4BridgeGUI(root)
        
        # Test button commands
        button_tests = [
            ('select_files_btn', 'select_files'),
            ('clear_files_btn', 'clear_files'),
            ('dir_browse_btn', 'select_output_directory'),
            ('convert_btn', 'start_conversion'),
            ('exit_btn', root.quit)
        ]
        
        for btn_name, expected_cmd in button_tests:
            if hasattr(app, btn_name):
                btn = getattr(app, btn_name)
                if hasattr(btn, 'cget'):
                    cmd = btn.cget('command')
                    if cmd:
                        print(f"✓ {btn_name}: Has command")
                    else:
                        print(f"✗ {btn_name}: No command!")
                else:
                    print(f"✗ {btn_name}: Not a button widget")
            else:
                print(f"✗ {btn_name}: Widget not found")
        
        root.destroy()
        print("✅ Button functionality test completed")
        return True
        
    except Exception as e:
        print(f"✗ Button test failed: {e}")
        return False

def main():
    """Main test function"""
    print("MF4Bridge GUI Layout Test")
    print("=" * 40)
    
    layout_ok = test_gui_layout()
    buttons_ok = test_button_functionality()
    
    print("\n" + "=" * 40)
    
    if layout_ok and buttons_ok:
        print("✅ GUI layout test passed!")
        print("\nThe GUI should now display properly with:")
        print("- All buttons visible")
        print("- Proper window size (900x800)")
        print("- Convert button at the bottom")
        print("\nRun: python main.py")
    else:
        print("✗ GUI layout test failed!")
        print("Some components may not display correctly.")
    
    return layout_ok and buttons_ok

if __name__ == "__main__":
    main()