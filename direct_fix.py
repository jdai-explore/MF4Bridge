#!/usr/bin/env python3
"""
Direct Fix for MF4Bridge Environment
Uses alternative installation methods to bypass pip path issues
"""

import subprocess
import sys
import importlib
import os
import tempfile
import urllib.request
import tarfile
import zipfile

def check_package(package_name):
    """Check if package is available and get version"""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, None

def run_command(command, description=""):
    """Run a command and return success status"""
    try:
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Success")
            return True
        else:
            print("✗ Failed")
            if result.stderr.strip():
                print(f"  Error: {result.stderr.strip().split('COPYING')[0][:200]}...")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def try_pip_install(package_spec, description=""):
    """Try multiple pip installation methods"""
    methods = [
        # Method 1: Standard pip
        [sys.executable, "-m", "pip", "install", package_spec],
        
        # Method 2: Pip with user flag
        [sys.executable, "-m", "pip", "install", "--user", package_spec],
        
        # Method 3: Pip with force reinstall
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-deps", package_spec],
        
        # Method 4: Direct python -m pip
        ["python3", "-m", "pip", "install", package_spec],
        
        # Method 5: System pip if available
        ["pip3", "install", package_spec],
    ]
    
    print(f"\n🔧 Installing {package_spec} ({description})...")
    
    for i, method in enumerate(methods, 1):
        print(f"\nMethod {i}: {' '.join(method)}")
        if run_command(method):
            return True
    
    return False

def install_numpy_manually():
    """Manually install compatible NumPy version"""
    print("\n🔧 Attempting manual NumPy installation...")
    
    # Try to use easy_install as fallback
    try:
        import setuptools
        print("✓ setuptools available")
        
        # Use easy_install for NumPy
        easy_install_cmd = [sys.executable, "-m", "easy_install", "numpy>=1.20.0,<2.0.0"]
        print(f"Trying easy_install: {' '.join(easy_install_cmd)}")
        
        result = subprocess.run(easy_install_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✓ NumPy installed via easy_install")
            return True
        else:
            print(f"✗ easy_install failed: {result.stderr[:100]}...")
    except ImportError:
        print("setuptools not available")
    
    return False

def check_pip_configuration():
    """Check pip configuration for issues"""
    print("\n🔍 Diagnosing pip configuration...")
    
    try:
        # Check pip version and configuration
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Pip version: {result.stdout.strip()}")
        
        # Check pip configuration
        result = subprocess.run([sys.executable, "-m", "pip", "config", "list"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print(f"Pip config: {result.stdout.strip()}")
        
        # Check if pip has hardcoded paths
        result = subprocess.run([sys.executable, "-c", 
                               "import pip; print(pip.__file__)"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Pip location: {result.stdout.strip()}")
            
    except Exception as e:
        print(f"Diagnosis failed: {e}")

def fix_environment_manually():
    """Manual environment fix using alternative methods"""
    print("🔧 Attempting manual environment fix...")
    
    # Try conda if available
    conda_commands = ["conda", "mamba", "micromamba"]
    for conda_cmd in conda_commands:
        try:
            result = subprocess.run([conda_cmd, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ Found {conda_cmd}: {result.stdout.strip()}")
                
                # Try to install via conda
                packages = ["numpy>=1.20,<2.0", "asammdf"]
                for package in packages:
                    conda_install = [conda_cmd, "install", "-y", package]
                    print(f"Trying: {' '.join(conda_install)}")
                    if run_command(conda_install):
                        print(f"✓ {package} installed via {conda_cmd}")
                
                return True
        except FileNotFoundError:
            continue
    
    # Try system package manager (macOS)
    try:
        # Check if brew is available
        result = subprocess.run(["brew", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ Homebrew available")
            
            # Try to install python packages via brew
            brew_packages = ["numpy", "python-tk"]
            for package in brew_packages:
                brew_cmd = ["brew", "install", f"python@3.13/{package}"]
                print(f"Trying: {' '.join(brew_cmd)}")
                run_command(brew_cmd)
                
    except FileNotFoundError:
        print("Homebrew not available")
    
    return False

def create_minimal_test():
    """Create a minimal test to check if basic functionality works"""
    print("\n🧪 Creating minimal functionality test...")
    
    test_code = '''
import sys
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
    print("✓ NumPy working")
except ImportError as e:
    print(f"✗ NumPy not available: {e}")

try:
    import tkinter
    print("✓ tkinter working")
except ImportError as e:
    print(f"✗ tkinter not available: {e}")

try:
    import asammdf
    print(f"asammdf: {asammdf.__version__}")
    print("✓ asammdf working")
except ImportError as e:
    print(f"✗ asammdf not available: {e}")

try:
    import customtkinter
    print(f"customtkinter: {customtkinter.__version__}")
    print("✓ customtkinter working")
except ImportError as e:
    print(f"✗ customtkinter not available: {e}")
'''
    
    try:
        with open('test_environment.py', 'w') as f:
            f.write(test_code)
        
        print("✓ Created test_environment.py")
        print("\nRunning environment test...")
        
        result = subprocess.run([sys.executable, 'test_environment.py'], 
                              capture_output=True, text=True, timeout=30)
        
        print("Test results:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
        return 'NumPy working' in result.stdout
        
    except Exception as e:
        print(f"Test creation failed: {e}")
        return False

def main():
    print("=" * 70)
    print("MF4Bridge Direct Environment Fix")
    print("=" * 70)
    
    print(f"Using Python: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check current state
    print(f"\n📦 Current package status:")
    packages = ['numpy', 'asammdf', 'customtkinter', 'tkinter']
    current_state = {}
    
    for package in packages:
        available, version = check_package(package)
        current_state[package] = (available, version)
        status = f"✓ {version}" if available else "✗ Not found"
        print(f"  {package}: {status}")
    
    # Diagnose pip issues
    check_pip_configuration()
    
    # Check if numpy needs fixing
    numpy_available, numpy_version = current_state['numpy']
    needs_numpy_fix = numpy_available and numpy_version and numpy_version.startswith('2.')
    
    if needs_numpy_fix:
        print(f"\n⚠️  NumPy 2.x detected ({numpy_version}) - attempting fix...")
        
        # Try different approaches
        success = False
        
        # Approach 1: Try standard pip methods
        if try_pip_install("numpy>=1.20.0,<2.0.0", "NumPy 1.x"):
            success = True
        
        # Approach 2: Manual installation
        if not success:
            success = install_numpy_manually()
        
        # Approach 3: Alternative package managers
        if not success:
            success = fix_environment_manually()
        
        if not success:
            print("❌ Could not fix NumPy automatically")
    
    # Try to install missing packages
    if not current_state['asammdf'][0]:
        print(f"\n📦 Installing asammdf...")
        try_pip_install("asammdf>=7.0.0", "MDF4 processing")
    
    if not current_state['customtkinter'][0]:
        print(f"\n📦 Installing customtkinter...")
        try_pip_install("customtkinter>=5.0.0", "Enhanced GUI")
    
    # Final test
    print(f"\n🧪 Running final environment test...")
    test_passed = create_minimal_test()
    
    print(f"\n" + "=" * 70)
    print("FINAL STATUS")
    print("=" * 70)
    
    if test_passed:
        print("✅ Basic environment working!")
        print("\n🚀 You can try running MF4Bridge:")
        print("python main.py")
        print("\n💡 If you get import errors, try:")
        print("python test_environment.py")
    else:
        print("❌ Environment still has issues")
        print("\n🔧 Manual fixes to try:")
        print("1. Reinstall Python 3.13 via Homebrew:")
        print("   brew uninstall python@3.13")
        print("   brew install python@3.13")
        print("\n2. Use conda/miniconda instead:")
        print("   conda create -n mf4bridge python=3.11")
        print("   conda activate mf4bridge")
        print("   conda install numpy asammdf")
        print("\n3. Use virtual environment:")
        print("   python3 -m venv mf4bridge_env")
        print("   source mf4bridge_env/bin/activate")
        print("   pip install numpy>=1.20.0,<2.0.0 asammdf")
    
    return test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)