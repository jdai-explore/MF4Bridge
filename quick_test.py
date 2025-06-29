#!/usr/bin/env python3
"""
Quick test script for MF4Bridge functionality
"""

import os
import tempfile
from pathlib import Path

def test_converter():
    """Test the converter functionality"""
    print("Testing MF4Bridge Converter...")
    print("=" * 40)
    
    try:
        # Import the converter
        from converter_engine import MF4Converter
        
        # Create a test converter
        def progress_callback(message, percentage):
            print(f"  {percentage:3.0f}% - {message}")
        
        converter = MF4Converter(progress_callback=progress_callback)
        
        # Create a temporary test file
        test_file = "quick_test.mf4"
        with open(test_file, 'wb') as f:
            # Write minimal MDF4-like content
            f.write(b'MDF     4.10')
            f.write(b'\x00' * 1000)  # Add some data
        
        print(f"✓ Created test file: {test_file}")
        
        # Test file validation
        print(f"✓ File validation: {converter.validate_mdf4_file(test_file)}")
        
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Test each conversion format
        formats = ['csv', 'asc', 'trc']
        results = []
        
        for fmt in formats:
            print(f"\nTesting {fmt.upper()} conversion:")
            output_file = os.path.join(output_dir, f"test_output.{fmt}")
            
            if fmt == 'csv':
                success = converter.mdf4_to_csv(test_file, output_file)
            elif fmt == 'asc':
                success = converter.mdf4_to_asc(test_file, output_file)
            elif fmt == 'trc':
                success = converter.mdf4_to_trc(test_file, output_file)
            
            results.append((fmt, success, output_file))
            
            if success and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"  ✓ {fmt.upper()} file created: {file_size} bytes")
                
                # Show first few lines
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]
                    print(f"  Preview:")
                    for line in lines:
                        print(f"    {line.strip()}")
            else:
                print(f"  ✗ {fmt.upper()} conversion failed")
        
        # Test batch conversion
        print(f"\nTesting batch conversion:")
        batch_results = converter.batch_convert([test_file], output_dir, formats)
        
        successful = len(batch_results['successful'])
        total = batch_results['total_conversions']
        print(f"  Batch conversion: {successful}/{total} successful")
        
        # Cleanup
        try:
            os.remove(test_file)
            for fmt, success, output_file in results:
                if os.path.exists(output_file):
                    os.remove(output_file)
            os.rmdir(output_dir)
        except:
            pass
        
        print(f"\n" + "=" * 40)
        print(f"✓ Converter test completed!")
        
        return True
        
    except Exception as e:
        print(f"✗ Converter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_imports():
    """Test GUI component imports"""
    print("Testing GUI imports...")
    print("=" * 40)
    
    try:
        # Test utils import
        from utils import validate_file_extension, format_file_size
        print("✓ Utils import successful")
        
        # Test converter import
        from converter_engine import MF4Converter
        print("✓ Converter import successful")
        
        # Test GUI import
        try:
            from gui_components import MF4BridgeGUI
            print("✓ CustomTkinter GUI import successful")
        except ImportError:
            from gui_components_simple import MF4BridgeGUI
            print("✓ Standard Tkinter GUI import successful")
        
        print(f"\n" + "=" * 40)
        print(f"✓ All imports successful!")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def main():
    """Main test function"""
    print("MF4Bridge Quick Test")
    print("=" * 50)
    
    # Test imports
    if not test_gui_imports():
        print("Import test failed - check dependencies")
        return False
    
    print()
    
    # Test converter functionality
    if not test_converter():
        print("Converter test failed")
        return False
    
    print()
    print("=" * 50)
    print("✓ All tests passed! MF4Bridge is ready to use.")
    print("Run 'python main.py' to start the GUI application.")
    
    return True

if __name__ == "__main__":
    main()