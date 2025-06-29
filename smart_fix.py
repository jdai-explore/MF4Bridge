#!/usr/bin/env python3
"""
Smart Fix for MF4Bridge Environment
Automatically detects the correct Python executable path
"""

import subprocess
import sys
import importlib
import os
import shutil

def find_working_python():
    """Find a working Python executable"""
    # List of possible Python executables to try
    candidates = [
        sys.executable,  # Current (may not work)
        '/usr/local/bin/python3',  # Common on macOS
        '/usr/bin/python3',  # System Python
        'python3',  # In PATH
        'python',  # In PATH
    ]
    
    # Also try to find python3 in PATH
    which_python = shutil.which('python3')
    if which_python:
        candidates.insert(1, which_python)
    
    which_python = shutil.which('python')
    if which_python:
        candidates.append(which_python)
    
    print("Testing Python executables...")
    
    for candidate in candidates:
        if not candidate:
            continue
            
        try:
            # Test if this Python executable works
            result = subprocess.run(
                [candidate, '-c', 'import sys; print(sys.version)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.strip()
                print(f"✓ Working Python found: {candidate}")
                print(f"  Version: {version_line}")
                return candidate
            else:
                print(f"✗ {candidate}: Failed (exit code {result.returncode})")
                
        except FileNotFoundError:
            print(f"✗ {candidate}: Not found")
        except Exception as e:
            print(f"✗ {candidate}: Error - {e}")
    
    return None

def run_pip_with_python(python_exe, command):
    """Run pip command with specific Python executable"""
    try:
        full_command = [python_exe, "-m", "pip"] + command
        print(f"Running: {' '.join(full_command)}")
        
        result = subprocess.run(full_command, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Success")
            # Only show relevant output
            output_lines = result.stdout.strip().split('\n')
            relevant_lines = [line for line in output_lines if 
                            'Successfully installed' in line or 
                            'Requirement already satisfied' in line or
                            'Collecting' in line]
            
            if relevant_lines:
                for line in relevant_lines[-3:]:  # Show last 3 relevant lines
                    print(f"  {line}")
            return True
        else:
            print("✗ Failed")
            if result.stderr.strip():
                # Show only the most relevant error lines
                error_lines = result.stderr.strip().split('\n')
                important_errors = [line for line in error_lines if 
                                  'ERROR' in line or 'error:' in line.lower()]
                
                if important_errors:
                    for line in important_errors[-2:]:  # Show last 2 error lines
                        print(f"  Error: {line}")
                else:
                    print(f"  Error: {error_lines[-1]}")  # Show last line
            return False
    except subprocess.TimeoutExpired:
        print("✗ Timeout (command took too long)")
        return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def check_package_with_python(python_exe, package_name):
    """Check if package is available with specific Python executable"""
    try:
        result = subprocess.run(
            [python_exe, '-c', f'import {package_name}; print({package_name}.__version__)'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        else:
            return False, None
            
    except Exception:
        return False, None

def main():
    print("=" * 70)
    print("MF4Bridge Smart Environment Fix")
    print("=" * 70)
    
    # Find working Python executable
    print("🔍 Finding working Python executable...")
    python_exe = find_working_python()
    
    if not python_exe:
        print("❌ No working Python executable found!")
        print("\nPlease ensure Python 3.8+ is properly installed.")
        return False
    
    print(f"\n✅ Using Python: {python_exe}")
    
    # Check current NumPy
    print(f"\n📦 Checking current packages...")
    numpy_available, numpy_version = check_package_with_python(python_exe, 'numpy')
    
    if numpy_available:
        print(f"Current NumPy: {numpy_version}")
        
        if numpy_version and numpy_version.startswith('2.'):
            print(f"\n⚠️  NumPy 2.x detected ({numpy_version}) - fixing compatibility...")
            print("This will downgrade NumPy to 1.x for asammdf compatibility")
            print("This may take a few minutes...")
            
            # Force reinstall compatible NumPy
            print(f"\n🔧 Installing compatible NumPy...")
            if run_pip_with_python(python_exe, ["install", "--upgrade", "--force-reinstall", "numpy>=1.20.0,<2.0.0"]):
                print("✅ NumPy downgraded successfully")
                
                # Verify the downgrade
                numpy_available, new_version = check_package_with_python(python_exe, 'numpy')
                if numpy_available:
                    print(f"✅ Verified: NumPy {new_version}")
                else:
                    print("⚠️  Could not verify NumPy installation")
            else:
                print("❌ Failed to downgrade NumPy")
                print("\nTrying alternative approach...")
                # Try uninstall first, then install
                print("Uninstalling NumPy 2.x...")
                run_pip_with_python(python_exe, ["uninstall", "-y", "numpy"])
                print("Installing NumPy 1.x...")
                if run_pip_with_python(python_exe, ["install", "numpy>=1.20.0,<2.0.0"]):
                    print("✅ NumPy installed via alternative method")
                else:
                    print("❌ Failed to install NumPy")
                    return False
        else:
            print("✅ NumPy version is compatible")
    else:
        print("NumPy not found - installing...")
        if run_pip_with_python(python_exe, ["install", "numpy>=1.20.0,<2.0.0"]):
            print("✅ NumPy installed")
        else:
            print("❌ Failed to install NumPy")
            return False
    
    # Install core dependencies
    print(f"\n📦 Installing core dependencies...")
    
    dependencies = [
        ("asammdf>=7.0.0", "MDF4 processing engine"),
        ("customtkinter>=5.0.0", "Enhanced GUI components")
    ]
    
    success_count = 0
    for dep_spec, description in dependencies:
        dep_name = dep_spec.split('>=')[0].split('==')[0]
        print(f"\n🔧 Installing {dep_name} ({description})...")
        
        if run_pip_with_python(python_exe, ["install", dep_spec]):
            print(f"✅ {dep_name} installed successfully")
            success_count += 1
        else:
            print(f"⚠️  Failed to install {dep_name}")
            # For core dependencies, try without version constraints
            if dep_name == "asammdf":
                print(f"Trying to install {dep_name} without version constraints...")
                if run_pip_with_python(python_exe, ["install", dep_name]):
                    print(f"✅ {dep_name} installed (fallback)")
                    success_count += 1
    
    # Verify installation
    print(f"\n🔍 Verifying installation...")
    
    packages_to_check = {
        'numpy': 'NumPy (numerical computing)',
        'asammdf': 'asammdf (MDF4 processing)',
        'customtkinter': 'CustomTkinter (enhanced GUI)'
    }
    
    working_packages = 0
    critical_packages = 0
    
    for package, description in packages_to_check.items():
        available, version = check_package_with_python(python_exe, package)
        if available:
            print(f"✅ {package}: {version} - {description}")
            working_packages += 1
            if package in ['numpy', 'asammdf']:
                critical_packages += 1
        else:
            print(f"❌ {package}: Not available - {description}")
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Python executable: {python_exe}")
    print(f"Packages working: {working_packages}/{len(packages_to_check)}")
    print(f"Critical packages: {critical_packages}/2")
    
    if critical_packages >= 1:  # At least numpy working
        print(f"\n✅ Environment setup complete!")
        if critical_packages == 2:
            print("🚀 Full MDF4 processing available")
        else:
            print("🔧 Demo mode available (asammdf missing)")
        
        print(f"\nYou can now run:")
        print(f"python main.py")
        print(f"# or")
        print(f"{python_exe} main.py")
        
        # Create a simple launcher script
        try:
            with open('run_mf4bridge.py', 'w') as f:
                f.write(f'#!/usr/bin/env python3\n')
                f.write(f'import subprocess\n')
                f.write(f'import sys\n\n')
                f.write(f'# Auto-generated launcher for MF4Bridge\n')
                f.write(f'python_exe = "{python_exe}"\n')
                f.write(f'subprocess.run([python_exe, "main.py"] + sys.argv[1:])\n')
            
            import stat
            os.chmod('run_mf4bridge.py', stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
            print(f"\n💡 Created launcher: run_mf4bridge.py")
            
        except Exception as e:
            print(f"\n⚠️  Could not create launcher: {e}")
        
        return True
    else:
        print(f"\n❌ Critical dependencies missing")
        print(f"Please check the error messages above and try manual installation:")
        print(f"{python_exe} -m pip install numpy>=1.20.0,<2.0.0")
        print(f"{python_exe} -m pip install asammdf>=7.0.0")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)