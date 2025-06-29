#!/usr/bin/env python3
"""
Quick Fix for MF4Bridge Environment
Resolves the immediate NumPy 2.x compatibility issue
"""

import subprocess
import sys
import importlib

def run_pip(command):
    """Run pip command with current Python executable"""
    try:
        full_command = [sys.executable, "-m", "pip"] + command
        print(f"Running: {' '.join(full_command)}")
        
        result = subprocess.run(full_command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Success")
            if result.stdout.strip():
                print(f"  Output: {result.stdout.strip()}")
            return True
        else:
            print("✗ Failed")
            if result.stderr.strip():
                print(f"  Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def check_package(package_name):
    """Check if package is available and get version"""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None

def main():
    print("=" * 60)
    print("MF4Bridge Quick Environment Fix")
    print("=" * 60)
    
    print(f"Using Python: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check current NumPy
    numpy_available, numpy_version = check_package('numpy')
    if numpy_available:
        print(f"Current NumPy: {numpy_version}")
        
        if numpy_version.startswith('2.'):
            print("\n⚠️  NumPy 2.x detected - fixing compatibility...")
            print("This will downgrade NumPy to 1.x for asammdf compatibility")
            
            # Force reinstall compatible NumPy
            print("\n1. Installing compatible NumPy...")
            if run_pip(["install", "--upgrade", "--force-reinstall", "numpy>=1.20.0,<2.0.0"]):
                print("✓ NumPy downgraded successfully")
            else:
                print("✗ Failed to downgrade NumPy")
                return False
        else:
            print("✓ NumPy version is compatible")
    else:
        print("NumPy not found - installing...")
        if run_pip(["install", "numpy>=1.20.0,<2.0.0"]):
            print("✓ NumPy installed")
        else:
            print("✗ Failed to install NumPy")
            return False
    
    # Install core dependencies
    print("\n2. Installing core dependencies...")
    
    dependencies = [
        "asammdf>=7.0.0",
        "customtkinter>=5.0.0"
    ]
    
    for dep in dependencies:
        print(f"\nInstalling {dep}...")
        if run_pip(["install", dep]):
            print(f"✓ {dep} installed successfully")
        else:
            print(f"⚠️ Failed to install {dep}")
    
    # Verify installation
    print("\n3. Verifying installation...")
    
    packages_to_check = {
        'numpy': 'NumPy (numerical computing)',
        'asammdf': 'asammdf (MDF4 processing)',
        'customtkinter': 'CustomTkinter (enhanced GUI)'
    }
    
    all_good = True
    for package, description in packages_to_check.items():
        available, version = check_package(package)
        if available:
            print(f"✓ {package}: {version} - {description}")
        else:
            print(f"✗ {package}: Not available - {description}")
            if package == 'asammdf':
                all_good = False
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ Environment setup complete!")
        print("\nYou can now run:")
        print("python main.py")
    else:
        print("⚠️  Some issues remain, but basic functionality should work")
        print("\nYou can try running in demo mode:")
        print("python main.py")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)