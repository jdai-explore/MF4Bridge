"""
MF4Bridge Enhanced Utility Functions
Comprehensive helper functions with improved error handling and logging
"""

import os
import sys
import tempfile
import shutil
import glob
import platform
from pathlib import Path
from typing import List, Union, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_file_extension(file_path: str, valid_extensions: List[str]) -> bool:
    """
    Validate if file has a valid extension
    
    Args:
        file_path: Path to the file
        valid_extensions: List of valid extensions (e.g., ['.mf4', '.MF4'])
        
    Returns:
        True if extension is valid, False otherwise
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        valid_exts_lower = [ext.lower() for ext in valid_extensions]
        return file_ext in valid_exts_lower
    except Exception as e:
        logger.warning(f"Error validating file extension for {file_path}: {e}")
        return False

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted size string (e.g., '1.5 MB')
    """
    if size_bytes == 0:
        return "0 B"
    
    try:
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size)} {size_names[i]}"
        else:
            return f"{size:.1f} {size_names[i]}"
            
    except Exception as e:
        logger.warning(f"Error formatting file size {size_bytes}: {e}")
        return f"{size_bytes} B"

def create_output_directory(directory_path: str) -> bool:
    """
    Create output directory if it doesn't exist
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ready: {directory_path}")
        return True
    except PermissionError:
        logger.error(f"Permission denied creating directory: {directory_path}")
        return False
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False

def get_safe_filename(filename: str) -> str:
    """
    Get a safe filename by removing or replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename string
    """
    try:
        # Characters not allowed in Windows filenames
        invalid_chars = '<>:"/\\|?*'
        
        safe_filename = filename
        for char in invalid_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Remove control characters
        safe_filename = ''.join(char for char in safe_filename if ord(char) >= 32)
        
        # Remove leading/trailing spaces and dots
        safe_filename = safe_filename.strip(' .')
        
        # Ensure filename is not empty and not too long
        if not safe_filename:
            safe_filename = "converted_file"
        elif len(safe_filename) > 255:
            # Truncate while preserving extension
            name, ext = os.path.splitext(safe_filename)
            max_name_length = 255 - len(ext)
            safe_filename = name[:max_name_length] + ext
        
        # Avoid reserved names on Windows
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = os.path.splitext(safe_filename)[0].upper()
        if name_without_ext in reserved_names:
            safe_filename = f"converted_{safe_filename}"
        
        return safe_filename
        
    except Exception as e:
        logger.warning(f"Error creating safe filename from '{filename}': {e}")
        return "converted_file"

def check_file_permissions(file_path: str) -> Dict[str, Any]:
    """
    Check file permissions for read/write access
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with permission status and file info
    """
    permissions = {
        'exists': False,
        'readable': False,
        'writable': False,
        'size': 0,
        'is_file': False,
        'is_directory': False,
        'last_modified': None,
        'error': None
    }
    
    try:
        if os.path.exists(file_path):
            permissions['exists'] = True
            permissions['readable'] = os.access(file_path, os.R_OK)
            permissions['writable'] = os.access(file_path, os.W_OK)
            permissions['is_file'] = os.path.isfile(file_path)
            permissions['is_directory'] = os.path.isdir(file_path)
            
            if permissions['is_file']:
                permissions['size'] = os.path.getsize(file_path)
                permissions['last_modified'] = os.path.getmtime(file_path)
                
    except Exception as e:
        permissions['error'] = str(e)
        logger.warning(f"Error checking permissions for {file_path}: {e}")
    
    return permissions

def get_unique_filename(file_path: str) -> str:
    """
    Get a unique filename by adding a number suffix if file already exists
    
    Args:
        file_path: Original file path
        
    Returns:
        Unique file path
    """
    try:
        if not os.path.exists(file_path):
            return file_path
        
        path_obj = Path(file_path)
        stem = path_obj.stem
        suffix = path_obj.suffix
        parent = path_obj.parent
        
        counter = 1
        while counter <= 9999:  # Prevent infinite loop
            new_name = f"{stem}_{counter:04d}{suffix}"
            new_path = parent / new_name
            
            if not os.path.exists(new_path):
                logger.info(f"Generated unique filename: {new_path}")
                return str(new_path)
            
            counter += 1
        
        # If we couldn't find a unique name, use timestamp
        import time
        timestamp = int(time.time())
        unique_name = f"{stem}_{timestamp}{suffix}"
        return str(parent / unique_name)
        
    except Exception as e:
        logger.error(f"Error generating unique filename for {file_path}: {e}")
        return file_path

def validate_output_directory(directory_path: str) -> Dict[str, Any]:
    """
    Validate output directory accessibility and permissions
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        'valid': False,
        'exists': False,
        'writable': False,
        'readable': False,
        'error_message': '',
        'free_space': 0,
        'absolute_path': ''
    }
    
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(directory_path)
        validation['absolute_path'] = abs_path
        
        # Check if directory exists
        if os.path.exists(abs_path):
            validation['exists'] = True
            
            # Check if it's actually a directory
            if not os.path.isdir(abs_path):
                validation['error_message'] = "Path exists but is not a directory"
                return validation
            
            # Check permissions
            validation['readable'] = os.access(abs_path, os.R_OK)
            validation['writable'] = os.access(abs_path, os.W_OK)
            
            if not validation['writable']:
                validation['error_message'] = "Directory is not writable"
                return validation
                
        else:
            # Try to create directory
            try:
                os.makedirs(abs_path, exist_ok=True)
                validation['exists'] = True
                validation['readable'] = True
                validation['writable'] = True
                logger.info(f"Created output directory: {abs_path}")
            except PermissionError:
                validation['error_message'] = "Permission denied: Cannot create directory"
                return validation
            except Exception as e:
                validation['error_message'] = f"Cannot create directory: {str(e)}"
                return validation
        
        # Check available disk space
        try:
            if hasattr(shutil, 'disk_usage'):
                total, used, free = shutil.disk_usage(abs_path)
                validation['free_space'] = free
            else:
                # Fallback for older Python versions
                statvfs = os.statvfs(abs_path) if hasattr(os, 'statvfs') else None
                if statvfs:
                    validation['free_space'] = statvfs.f_bavail * statvfs.f_frsize
        except Exception as e:
            logger.debug(f"Could not determine free space: {e}")
            validation['free_space'] = -1  # Unknown
        
        validation['valid'] = True
        
    except Exception as e:
        validation['error_message'] = f"Error validating directory: {str(e)}"
        logger.error(f"Directory validation error for {directory_path}: {e}")
    
    return validation

def get_application_path() -> str:
    """
    Get the path where the application is running from
    
    Returns:
        Application directory path
    """
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_path = os.path.dirname(os.path.abspath(__file__))
        
        logger.debug(f"Application path: {app_path}")
        return app_path
        
    except Exception as e:
        logger.error(f"Error determining application path: {e}")
        return os.getcwd()

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    try:
        # Create logs directory if needed
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                logger.info(f"Logging to file: {log_file}")
            except Exception as e:
                logger.warning(f"Could not set up file logging: {e}")
        
        return root_logger
        
    except Exception as e:
        print(f"Error setting up logging: {e}")
        return logging.getLogger()

def log_conversion_result(file_path: str, format_type: str, success: bool, 
                         error_msg: Optional[str] = None, output_size: int = 0):
    """
    Log conversion results to a log file with detailed information
    
    Args:
        file_path: Input file path
        format_type: Output format type
        success: Whether conversion was successful
        error_msg: Error message if conversion failed
        output_size: Size of output file in bytes
    """
    try:
        log_file = os.path.join(get_application_path(), "logs", "conversion.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "a", encoding="utf-8") as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "SUCCESS" if success else "FAILED"
            
            log_entry = f"[{timestamp}] {status}: {os.path.basename(file_path)} → {format_type.upper()}"
            
            if success and output_size > 0:
                log_entry += f" ({format_file_size(output_size)})"
            
            if not success and error_msg:
                log_entry += f" - Error: {error_msg}"
            
            f.write(log_entry + "\n")
            
    except Exception as e:
        logger.debug(f"Could not write to conversion log: {e}")

def cleanup_temp_files(temp_directory: Optional[str] = None, max_age_hours: int = 24):
    """
    Clean up temporary files created during conversion
    
    Args:
        temp_directory: Optional specific directory to clean
        max_age_hours: Maximum age of temp files to keep (in hours)
    """
    try:
        import time
        
        if temp_directory:
            temp_patterns = [
                os.path.join(temp_directory, "mf4bridge_temp_*"),
                os.path.join(temp_directory, "*.tmp")
            ]
        else:
            temp_dir = tempfile.gettempdir()
            temp_patterns = [
                os.path.join(temp_dir, "mf4bridge_temp_*"),
                os.path.join(temp_dir, "mf4bridge_*.tmp")
            ]
        
        files_cleaned = 0
        bytes_freed = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for pattern in temp_patterns:
            temp_files = glob.glob(pattern)
            
            for temp_file in temp_files:
                try:
                    # Check file age
                    file_age = current_time - os.path.getmtime(temp_file)
                    if file_age < max_age_seconds:
                        continue  # Skip recent files
                    
                    file_size = 0
                    if os.path.isfile(temp_file):
                        file_size = os.path.getsize(temp_file)
                        os.remove(temp_file)
                    elif os.path.isdir(temp_file):
                        file_size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(temp_file)
                            for filename in filenames
                        )
                        shutil.rmtree(temp_file)
                    
                    files_cleaned += 1
                    bytes_freed += file_size
                    
                except Exception as e:
                    logger.debug(f"Could not clean temp file {temp_file}: {e}")
                    continue
        
        if files_cleaned > 0:
            logger.info(f"Cleaned {files_cleaned} temp files, freed {format_file_size(bytes_freed)}")
        
    except Exception as e:
        logger.debug(f"Temp file cleanup failed: {e}")

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information for debugging purposes
    
    Returns:
        Dictionary with system information
    """
    info = {
        'platform': 'unknown',
        'python_version': 'unknown',
        'architecture': 'unknown',
        'machine': 'unknown',
        'processor': 'unknown',
        'memory_total': 0,
        'memory_available': 0,
        'disk_space_free': 0,
        'environment': {}
    }
    
    try:
        info['platform'] = platform.platform()
        info['python_version'] = platform.python_version()
        info['architecture'] = platform.architecture()[0]
        info['machine'] = platform.machine()
        info['processor'] = platform.processor()
        
        # Memory information (if psutil is available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            info['memory_total'] = memory.total
            info['memory_available'] = memory.available
            
            disk = psutil.disk_usage(os.getcwd())
            info['disk_space_free'] = disk.free
        except ImportError:
            logger.debug("psutil not available for detailed system info")
        
        # Relevant environment variables
        env_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER', 'USERNAME', 'TEMP', 'TMP']
        for var in env_vars:
            if var in os.environ:
                info['environment'][var] = os.environ[var]
        
    except Exception as e:
        logger.warning(f"Error collecting system info: {e}")
    
    return info

def check_dependencies() -> Dict[str, Any]:
    """
    Check for required and optional dependencies
    
    Returns:
        Dictionary with dependency status
    """
    dependencies = {
        'required': {},
        'optional': {},
        'all_satisfied': True
    }
    
    # Required dependencies
    required_deps = {
        'tkinter': 'GUI framework',
        'pathlib': 'Path operations',
        'csv': 'CSV file operations',
        'threading': 'Multi-threading support'
    }
    
    # Optional dependencies  
    optional_deps = {
        'asammdf': 'MDF4 file processing',
        'customtkinter': 'Enhanced GUI components',
        'numpy': 'Numerical computations',
        'psutil': 'System information'
    }
    
    for dep_name, description in required_deps.items():
        try:
            __import__(dep_name)
            dependencies['required'][dep_name] = {
                'available': True,
                'version': 'built-in' if dep_name in ['tkinter', 'pathlib', 'csv', 'threading'] else 'unknown',
                'description': description
            }
        except ImportError:
            dependencies['required'][dep_name] = {
                'available': False,
                'version': None,
                'description': description
            }
            dependencies['all_satisfied'] = False
    
    for dep_name, description in optional_deps.items():
        try:
            module = __import__(dep_name)
            version = getattr(module, '__version__', 'unknown')
            dependencies['optional'][dep_name] = {
                'available': True,
                'version': version,
                'description': description
            }
        except ImportError:
            dependencies['optional'][dep_name] = {
                'available': False,
                'version': None,
                'description': description
            }
    
    return dependencies

def create_backup(file_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """
    Create a backup of a file before overwriting
    
    Args:
        file_path: Path to file to backup
        backup_dir: Optional backup directory (default: same directory as file)
        
    Returns:
        Path to backup file, or None if backup failed
    """
    try:
        if not os.path.exists(file_path):
            return None
            
        # Determine backup directory
        if backup_dir is None:
            backup_dir = os.path.dirname(file_path)
        else:
            os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(file_path).name
        backup_name = f"{file_name}.backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return None