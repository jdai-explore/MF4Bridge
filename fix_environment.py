#!/usr/bin/env python3
"""
MF4Bridge Environment Fix
Resolve NumPy compatibility issues and set up proper environment
"""

import subprocess
import sys
import os
import importlib.util

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {command}")
            return True
        else:
            print(f"✗ {command}")
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ {command} - Exception: {e}")
        return False

def check_package_version(package_name):
    """Check if a package is installed and get its version"""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None

def main():
    """Main environment fixing function"""
    print("MF4Bridge Environment Setup & Repair")
    print("=" * 50)
    
    # Step 1: Check current NumPy version
    numpy_installed, numpy_version = check_package_version('numpy')
    if numpy_installed:
        print(f"Current NumPy version: {numpy_version}")
        if numpy_version.startswith('2.'):
            print("⚠️  NumPy 2.x detected - this causes compatibility issues")
            print("   Downgrading to NumPy 1.x for compatibility...")
            
            # Uninstall problematic packages
            print("\n1. Removing incompatible packages...")
            run_command("pip uninstall -y numpy pandas pyarrow asammdf")
            
            # Install compatible versions
            print("\n2. Installing compatible versions...")
            compatible_packages = [
                "numpy<2.0.0",
                "pandas>=1.5.0,<3.0.0", 
                "pyarrow>=10.0.0,<16.0.0",
                "asammdf>=7.0.0,<8.0.0"
            ]
            
            for package in compatible_packages:
                run_command(f"pip install '{package}'")
        else:
            print("✓ NumPy 1.x detected - compatible version")
    else:
        print("NumPy not found - installing compatible version...")
        run_command("pip install 'numpy<2.0.0'")
    
    # Step 2: Install optional GUI dependencies
    print("\n3. Installing optional GUI components...")
    run_command("pip install customtkinter")
    
    # Step 3: Verify installation
    print("\n4. Verifying installation...")
    packages_to_check = ['numpy', 'pandas', 'asammdf', 'customtkinter']
    
    all_good = True
    for package in packages_to_check:
        installed, version = check_package_version(package)
        if installed:
            print(f"✓ {package}: {version}")
        else:
            print(f"✗ {package}: Not installed")
            all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("✓ Environment setup complete!")
        print("\nYou can now run MF4Bridge:")
        print("python main.py")
    else:
        print("✗ Some issues remain. Try manual installation:")
        print("pip install numpy==1.24.4 pandas==2.1.4 asammdf==7.4.2 customtkinter")
    
    return all_good

if __name__ == "__main__":
    main()