#!/usr/bin/env python3
"""
MF4Bridge - Enhanced MDF4 File Converter
Main application entry point with responsive design and robust error handling
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
import signal
import atexit
from pathlib import Path

# Configure comprehensive logging
def setup_logging():
    """Setup enhanced logging configuration"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "mf4bridge.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_python_version():
    """Ensure minimum Python version requirement with detailed info"""
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        error_msg = (
            f"Python {min_version[0]}.{min_version[1]}+ required.\n"
            f"Current version: {sys.version}\n"
            f"Please upgrade Python to continue."
        )
        logger.error(error_msg)
        try:
            messagebox.showerror("Python Version Error", error_msg)
        except:
            print(error_msg)
        return False
    
    logger.info(f"✓ Python {sys.version.split()[0]} - compatible")
    return True

def check_dependencies():
    """Enhanced dependency checking with performance info"""
    missing_deps = []
    optional_deps = []
    
    # Check for asammdf (core functionality)
    try:
        import asammdf
        logger.info(f"✓ asammdf {asammdf.__version__} found")
    except ImportError:
        logger.warning("✗ asammdf not found - will run in demo mode")
        missing_deps.append('asammdf')
    
    # Check for NumPy compatibility
    try:
        import numpy as np
        numpy_version = np.__version__
        if numpy_version.startswith('2.'):
            logger.warning(f"⚠️ NumPy 2.x detected ({numpy_version}) - may cause compatibility issues")
            logger.info("Consider running: pip install 'numpy>=1.20.0,<2.0.0'")
        else:
            logger.info(f"✓ NumPy {numpy_version} - compatible")
    except ImportError:
        logger.warning("✗ NumPy not found - required for asammdf")
        missing_deps.append('numpy')
    
    # Check for CustomTkinter (optional, for better UI)
    try:
        import customtkinter
        logger.info(f"✓ CustomTkinter {customtkinter.__version__} found - enhanced UI available")
    except ImportError:
        logger.info("ℹ CustomTkinter not found - using standard tkinter")
        optional_deps.append('customtkinter')
    
    # Check system resources
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        logger.info(f"✓ System memory: {memory_gb:.1f}GB")
        if memory_gb < 2:
            logger.warning("⚠️ Low system memory detected - may affect large file processing")
    except ImportError:
        logger.debug("psutil not available - cannot check system resources")
    
    return missing_deps, optional_deps

def handle_startup_error(error_type: str, error_msg: str, show_gui: bool = True):
    """Handle startup errors with appropriate user feedback"""
    full_msg = f"{error_type}: {error_msg}"
    logger.error(full_msg)
    
    if show_gui:
        try:
            # Create minimal root window for error display
            error_root = tk.Tk()
            error_root.withdraw()
            messagebox.showerror(error_type, full_msg)
            error_root.destroy()
        except:
            print(full_msg)
    else:
        print(full_msg)

def create_gui():
    """Create and return the appropriate GUI instance with error handling"""
    try:
        # Try CustomTkinter first if available
        try:
            import customtkinter as ctk
            from gui_components import MF4BridgeGUI
            
            # Set appearance mode and theme
            ctk.set_appearance_mode("system")
            ctk.set_default_color_theme("blue")
            
            root = ctk.CTk()
            logger.info("✓ Using CustomTkinter interface")
            
        except ImportError:
            # Fall back to standard tkinter
            from gui_components import MF4BridgeGUI
            root = tk.Tk()
            logger.info("✓ Using standard Tkinter interface")
        
        # Configure root window properties
        root.title("MF4Bridge - Starting...")
        
        # Handle high-DPI displays
        try:
            root.tk.call('tk', 'scaling', '-displayof', '.', 1.0)
        except:
            pass
        
        # Initialize the application
        app = MF4BridgeGUI(root)
        
        # Update title after successful initialization
        root.title("MF4Bridge - MDF4 File Converter")
        
        return root, app
        
    except Exception as e:
        logger.error(f"Failed to create GUI: {e}", exc_info=True)
        raise

def show_dependency_info(missing_deps, optional_deps):
    """Show enhanced information about missing dependencies"""
    if not missing_deps:
        return None
    
    def show_info():
        message_parts = ["MF4Bridge is running in demo mode.\n"]
        
        if missing_deps:
            message_parts.append("Missing core dependencies:")
            for dep in missing_deps:
                if dep == 'asammdf':
                    message_parts.append("  • asammdf - Required for real MDF4 file processing")
                elif dep == 'numpy':
                    message_parts.append("  • numpy - Required for numerical computations")
                else:
                    message_parts.append(f"  • {dep}")
            message_parts.append("")
        
        message_parts.extend([
            "Demo mode features:",
            "  ✅ Test all functionality with realistic sample data",
            "  ✅ Learn the interface and workflow", 
            "  ✅ Verify output formats and file structure",
            "  ⚠️ Real MDF4 files won't be processed",
            "",
            "To enable full functionality, install dependencies:",
            "  Option 1: pip install asammdf>=7.0.0",
            "  Option 2: Run setup_environment.py",
            "  Option 3: Run smart_fix.py for automatic setup",
            "",
            "For enhanced GUI (optional):",
            "  pip install customtkinter>=5.0.0",
            "",
            "Would you like to continue in demo mode?"
        ])
        
        result = messagebox.askyesno(
            "Demo Mode - Enhanced MF4Bridge", 
            "\n".join(message_parts)
        )
        
        if not result:
            logger.info("User chose to exit and install dependencies")
            sys.exit(0)
    
    return show_info

def setup_signal_handlers(root, app=None):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        
        if app and hasattr(app, 'cancel_conversion'):
            app.cancel_conversion()
        
        if root:
            try:
                root.quit()
            except:
                pass
        
        sys.exit(0)
    
    # Setup signal handlers for Unix-like systems
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

def setup_cleanup():
    """Setup cleanup functions for application exit"""
    def cleanup_on_exit():
        try:
            # Cleanup temporary files
            from utils import cleanup_temp_files
            cleanup_temp_files()
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.debug(f"Cleanup failed: {e}")
    
    atexit.register(cleanup_on_exit)

def check_system_compatibility():
    """Check system compatibility and warn about potential issues"""
    warnings = []
    
    try:
        # Check available disk space
        import shutil
        free_space = shutil.disk_usage(".").free
        free_gb = free_space / (1024**3)
        
        if free_gb < 1:
            warnings.append(f"Low disk space: {free_gb:.1f}GB available")
        
        # Check if running in virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("✓ Running in virtual environment")
        else:
            logger.info("ℹ Running in system Python environment")
        
        # Platform-specific checks
        import platform
        system = platform.system()
        logger.info(f"✓ Platform: {system} {platform.release()}")
        
        if system == "Darwin":  # macOS
            # Check for potential tkinter issues on macOS
            try:
                root = tk.Tk()
                root.withdraw()
                root.destroy()
            except Exception as e:
                warnings.append("Tkinter GUI may have issues on this macOS version")
        
        if warnings:
            for warning in warnings:
                logger.warning(f"⚠️ {warning}")
                
    except Exception as e:
        logger.debug(f"System compatibility check failed: {e}")

def main():
    """Enhanced main application entry point"""
    logger.info("=" * 70)
    logger.info("Starting MF4Bridge Enhanced")
    logger.info("=" * 70)
    
    try:
        # System compatibility check
        check_system_compatibility()
        
        # Check Python version
        if not check_python_version():
            sys.exit(1)
        
        # Setup cleanup handlers
        setup_cleanup()
        
        # Check dependencies
        missing_deps, optional_deps = check_dependencies()
        
        # Log startup information
        logger.info(f"Application path: {os.path.dirname(os.path.abspath(__file__))}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Create GUI with enhanced error handling
        try:
            root, app = create_gui()
        except ImportError as e:
            handle_startup_error(
                "Import Error",
                f"Failed to import required modules: {str(e)}\n"
                f"Try running: pip install tkinter",
                show_gui=False
            )
            sys.exit(1)
        except Exception as e:
            handle_startup_error(
                "GUI Creation Error", 
                f"Failed to create application interface: {str(e)}"
            )
            sys.exit(1)
        
        # Setup signal handlers
        setup_signal_handlers(root, app)
        
        # Show dependency info if needed (after GUI loads)
        if missing_deps:
            demo_info_func = show_dependency_info(missing_deps, optional_deps)
            if demo_info_func:
                root.after(1500, demo_info_func)  # Show after 1.5 seconds
        
        # Log successful startup
        logger.info("✅ MF4Bridge Enhanced started successfully")
        logger.info(f"GUI Framework: {'CustomTkinter' if 'customtkinter' in sys.modules else 'Standard Tkinter'}")
        logger.info(f"Mode: {'Full' if not missing_deps else 'Demo'}")
        
        # Start the main event loop with error handling
        try:
            root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"Error in main event loop: {e}", exc_info=True)
            handle_startup_error("Runtime Error", f"Application error: {str(e)}")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user during startup")
        sys.exit(0)
        
    except Exception as e:
        error_msg = f"Failed to start MF4Bridge Enhanced: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        handle_startup_error("Startup Error", error_msg)
        sys.exit(1)
    
    finally:
        logger.info("MF4Bridge Enhanced shutdown complete")

if __name__ == "__main__":
    main()