#!/usr/bin/env python3
"""
MF4Bridge Dependency Installer
Automatically install required dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """Check if a package is already installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """Main installation function"""
    print("MF4Bridge Dependency Installer")
    print("=" * 40)
    
    # Required packages
    packages = {
        'asammdf': 'asammdf>=7.0.0',
        'customtkinter': 'customtkinter>=5.0.0'
    }
    
    all_installed = True
    
    for package_name, package_spec in packages.items():
        print(f"Checking {package_name}...", end=" ")
        
        if check_package(package_name):
            print("✓ Already installed")
        else:
            print("✗ Not found - Installing...")
            if install_package(package_spec):
                print(f"✓ {package_name} installed successfully")
            else:
                print(f"✗ Failed to install {package_name}")
                all_installed = False
    
    print("\n" + "=" * 40)
    
    if all_installed:
        print("✓ All dependencies installed successfully!")
        print("\nYou can now run MF4Bridge:")
        print("python main.py")
    else:
        print("✗ Some dependencies failed to install.")
        print("\nTry manual installation:")
        print("pip install asammdf customtkinter")
        
    return all_installed

if __name__ == "__main__":
    main()