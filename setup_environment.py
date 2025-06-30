#!/usr/bin/env python3
"""
MF4Bridge Environment Setup: Script for dependency management and environment configuration
Author: Jayadev Meka Name
Date: 2025-06-24
Version: 1.1
License: MIT
"""

import subprocess
import sys
import os
import importlib.util
import logging
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DependencyManager:
    """Manages dependencies for MF4Bridge"""
    
    def __init__(self):
        self.required_packages = {
            'asammdf': {
                'version': '>=7.0.0',
                'description': 'MDF4 file processing',
                'critical': True,
                'fallback': 'Demo mode will be used'
            }
        }
        
        self.optional_packages = {
            'customtkinter': {
                'version': '>=5.0.0',
                'description': 'Enhanced GUI components',
                'critical': False,
                'fallback': 'Standard tkinter will be used'
            },
            'numpy': {
                'version': '>=1.20.0,<2.0.0',
                'description': 'Numerical computations (asammdf dependency)',
                'critical': False,
                'fallback': 'May cause issues with asammdf'
            },
            'pandas': {
                'version': '>=1.5.0,<3.0.0',
                'description': 'Data manipulation (asammdf dependency)',
                'critical': False,
                'fallback': 'May cause issues with asammdf'
            }
        }
        
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements"""
        min_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version < min_version:
            logger.error(f"Python {min_version[0]}.{min_version[1]}+ required. Current: {sys.version}")
            return False
        
        logger.info(f"✓ Python {sys.version.split()[0]} - compatible")
        logger.info(f"Using Python executable: {sys.executable}")
        return True
    
    def check_package_availability(self, package_name: str) -> Tuple[bool, Optional[str]]:
        """Check if a package is available and get its version"""
        try:
            spec = importlib.util.find_spec(package_name)
            if spec is None:
                return False, None
                
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            return True, version
            
        except ImportError:
            return False, None
        except Exception as e:
            logger.debug(f"Error checking {package_name}: {e}")
            return False, None
    
    def run_pip_command(self, command: List[str]) -> bool:
        """Run a pip command safely"""
        try:
            # Use the current Python executable (the one running this script)
            python_exe = sys.executable
            full_command = [python_exe, "-m", "pip"] + command
            logger.info(f"Running: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.debug(f"Command output: {result.stdout}")
                if result.stdout:
                    logger.info(f"Success: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"Command failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr.strip()}")
                if result.stdout:
                    logger.error(f"Standard output: {result.stdout.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Pip command timed out after 5 minutes")
            return False
        except FileNotFoundError as e:
            logger.error(f"Python executable not found: {e}")
            logger.error(f"Tried to use: {sys.executable}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error running pip command: {e}")
            return False
    
    def install_package(self, package_name: str, version_spec: str) -> bool:
        """Install a specific package with version specification"""
        package_spec = f"{package_name}{version_spec}"
        
        logger.info(f"Installing {package_spec}...")
        
        # Try to install the package
        if self.run_pip_command(["install", package_spec]):
            logger.info(f"✓ Successfully installed {package_name}")
            return True
        else:
            logger.error(f"✗ Failed to install {package_name}")
            return False
    
    def uninstall_package(self, package_name: str) -> bool:
        """Uninstall a package"""
        logger.info(f"Uninstalling {package_name}...")
        
        if self.run_pip_command(["uninstall", "-y", package_name]):
            logger.info(f"✓ Successfully uninstalled {package_name}")
            return True
        else:
            logger.warning(f"⚠ Could not uninstall {package_name} (may not be installed)")
            return False
    
    def fix_numpy_compatibility(self) -> bool:
        """Fix NumPy 2.x compatibility issues"""
        numpy_available, numpy_version = self.check_package_availability('numpy')
        
        if not numpy_available:
            logger.info("NumPy not found - installing compatible version")
            return self.install_package('numpy', '>=1.20.0,<2.0.0')
        
        logger.info(f"Current NumPy version: {numpy_version}")
        
        if numpy_version and numpy_version.startswith('2.'):
            logger.warning(f"NumPy 2.x detected ({numpy_version}) - downgrading for compatibility")
            logger.info("This may take a few minutes...")
            
            # For NumPy 2.x, we need to force reinstall with compatible versions
            logger.info("Installing compatible NumPy version...")
            if not self.run_pip_command(["install", "--upgrade", "--force-reinstall", "numpy>=1.20.0,<2.0.0"]):
                logger.error("Failed to downgrade NumPy")
                return False
            
            # Check if we need to reinstall pandas and asammdf
            pandas_available, pandas_version = self.check_package_availability('pandas')
            if pandas_available:
                logger.info("Reinstalling pandas for NumPy compatibility...")
                if not self.run_pip_command(["install", "--upgrade", "--force-reinstall", "pandas>=1.5.0,<3.0.0"]):
                    logger.warning("Failed to reinstall pandas - may cause issues")
            
            asammdf_available, asammdf_version = self.check_package_availability('asammdf')
            if asammdf_available:
                logger.info("Reinstalling asammdf for NumPy compatibility...")
                if not self.run_pip_command(["install", "--upgrade", "--force-reinstall", "asammdf>=7.0.0"]):
                    logger.warning("Failed to reinstall asammdf - may cause issues")
            
            # Verify the fix worked
            numpy_available, new_numpy_version = self.check_package_availability('numpy')
            if numpy_available and new_numpy_version:
                logger.info(f"✓ NumPy downgraded to {new_numpy_version}")
                return True
            else:
                logger.error("NumPy downgrade verification failed")
                return False
        else:
            logger.info(f"✓ NumPy {numpy_version} - compatible version")
            return True
    
    def check_all_dependencies(self) -> Dict[str, Dict]:
        """Check status of all dependencies"""
        status = {
            'required': {},
            'optional': {},
            'summary': {
                'all_required_met': True,
                'missing_required': [],
                'missing_optional': []
            }
        }
        
        # Check required packages
        for package, info in self.required_packages.items():
            available, version = self.check_package_availability(package)
            status['required'][package] = {
                'available': available,
                'version': version,
                'info': info
            }
            
            if not available and info['critical']:
                status['summary']['all_required_met'] = False
                status['summary']['missing_required'].append(package)
        
        # Check optional packages
        for package, info in self.optional_packages.items():
            available, version = self.check_package_availability(package)
            status['optional'][package] = {
                'available': available,
                'version': version,
                'info': info
            }
            
            if not available:
                status['summary']['missing_optional'].append(package)
        
        return status
    
    def install_missing_dependencies(self, install_optional: bool = True) -> bool:
        """Install missing dependencies"""
        logger.info("Installing missing dependencies...")
        
        success = True
        
        # Install required packages
        for package, info in self.required_packages.items():
            available, _ = self.check_package_availability(package)
            if not available:
                if not self.install_package(package, info['version']):
                    success = False
        
        # Install optional packages if requested
        if install_optional:
            for package, info in self.optional_packages.items():
                available, _ = self.check_package_availability(package)
                if not available:
                    if not self.install_package(package, info['version']):
                        logger.warning(f"Could not install optional package {package}")
                        # Don't mark as failure for optional packages
        
        return success
    
    def setup_environment(self, fix_numpy: bool = True, install_optional: bool = True) -> bool:
        """Complete environment setup"""
        logger.info("=" * 60)
        logger.info("MF4Bridge Environment Setup")
        logger.info("=" * 60)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Fix NumPy compatibility if requested
        if fix_numpy:
            logger.info("\n1. Checking NumPy compatibility...")
            if not self.fix_numpy_compatibility():
                logger.error("Failed to fix NumPy compatibility")
                return False
        
        # Check current dependency status
        logger.info("\n2. Checking dependencies...")
        status = self.check_all_dependencies()
        
        # Report current status
        self.report_dependency_status(status)
        
        # Install missing dependencies
        if status['summary']['missing_required'] or (install_optional and status['summary']['missing_optional']):
            logger.info("\n3. Installing missing dependencies...")
            if not self.install_missing_dependencies(install_optional):
                logger.error("Failed to install some dependencies")
                return False
        else:
            logger.info("\n3. All dependencies satisfied!")
        
        # Final verification
        logger.info("\n4. Final verification...")
        final_status = self.check_all_dependencies()
        self.report_dependency_status(final_status)
        
        # Summary
        logger.info("\n" + "=" * 60)
        if final_status['summary']['all_required_met']:
            logger.info("✅ Environment setup completed successfully!")
            logger.info("You can now run: python main.py")
        else:
            logger.warning("⚠️ Some required dependencies are still missing")
            logger.info("MF4Bridge will run in demo mode")
        
        return final_status['summary']['all_required_met']
    
    def report_dependency_status(self, status: Dict) -> None:
        """Report the current dependency status"""
        logger.info("\nDependency Status:")
        logger.info("-" * 40)
        
        # Required dependencies
        logger.info("Required:")
        for package, pkg_status in status['required'].items():
            if pkg_status['available']:
                logger.info(f"  ✓ {package}: {pkg_status['version']}")
            else:
                logger.info(f"  ✗ {package}: not found")
                logger.info(f"    → {pkg_status['info']['fallback']}")
        
        # Optional dependencies
        logger.info("\nOptional:")
        for package, pkg_status in status['optional'].items():
            if pkg_status['available']:
                logger.info(f"  ✓ {package}: {pkg_status['version']}")
            else:
                logger.info(f"  - {package}: not found")
                logger.info(f"    → {pkg_status['info']['fallback']}")

def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MF4Bridge Environment Setup')
    parser.add_argument('--no-numpy-fix', action='store_true', 
                       help='Skip NumPy compatibility fixes')
    parser.add_argument('--no-optional', action='store_true',
                       help='Skip optional dependencies')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check dependencies, do not install')
    
    args = parser.parse_args()
    
    manager = DependencyManager()
    
    if args.check_only:
        logger.info("Dependency Check Mode")
        logger.info("=" * 40)
        status = manager.check_all_dependencies()
        manager.report_dependency_status(status)
        
        if status['summary']['all_required_met']:
            logger.info("\n✅ All required dependencies are satisfied")
            sys.exit(0)
        else:
            logger.info("\n❌ Some required dependencies are missing")
            logger.info("Run without --check-only to install them")
            sys.exit(1)
    else:
        success = manager.setup_environment(
            fix_numpy=not args.no_numpy_fix,
            install_optional=not args.no_optional
        )
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()