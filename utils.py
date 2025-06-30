"""
MF4Bridge Utility Functions: Optimized helper functions with performance improvements and error handling
Author: Jayadev Meka Name
Date: 2025-06-30
Version: 1.2
License: MIT
"""

import os
import sys
import tempfile
import shutil
import glob
import platform
import threading
import time
import hashlib
from pathlib import Path
from typing import List, Union, Dict, Any, Optional, Tuple, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        logger.debug(f"Operation '{self.operation_name}' took {duration:.3f}s")

class FileValidator:
    """Enhanced file validation with caching"""
    
    def __init__(self):
        self._validation_cache = {}
        self._cache_lock = threading.Lock()
        
    def validate_file_extension(self, file_path: str, valid_extensions: List[str]) -> bool:
        """
        Validate if file has a valid extension with caching
        
        Args:
            file_path: Path to the file
            valid_extensions: List of valid extensions (e.g., ['.mf4', '.MF4'])
            
        Returns:
            True if extension is valid, False otherwise
        """
        try:
            # Use cache for repeated validations
            cache_key = (file_path, tuple(sorted(ext.lower() for ext in valid_extensions)))
            
            with self._cache_lock:
                if cache_key in self._validation_cache:
                    return self._validation_cache[cache_key]
            
            file_ext = Path(file_path).suffix.lower()
            valid_exts_lower = [ext.lower() for ext in valid_extensions]
            result = file_ext in valid_exts_lower
            
            with self._cache_lock:
                self._validation_cache[cache_key] = result
                # Limit cache size
                if len(self._validation_cache) > 1000:
                    # Remove oldest entries
                    keys_to_remove = list(self._validation_cache.keys())[:100]
                    for key in keys_to_remove:
                        del self._validation_cache[key]
            
            return result
            
        except Exception as e:
            logger.warning(f"Error validating file extension for {file_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        info = {
            'exists': False,
            'size': 0,
            'size_formatted': '0 B',
            'readable': False,
            'writable': False,
            'last_modified': None,
            'extension': '',
            'is_binary': False,
            'hash_md5': None
        }
        
        try:
            if os.path.exists(file_path):
                info['exists'] = True
                info['readable'] = os.access(file_path, os.R_OK)
                info['writable'] = os.access(file_path, os.W_OK)
                
                if os.path.isfile(file_path):
                    stat_info = os.stat(file_path)
                    info['size'] = stat_info.st_size
                    info['size_formatted'] = format_file_size(info['size'])
                    info['last_modified'] = stat_info.st_mtime
                    info['extension'] = Path(file_path).suffix.lower()
                    
                    # Check if binary file (simple heuristic)
                    if info['size'] > 0:
                        try:
                            with open(file_path, 'rb') as f:
                                chunk = f.read(1024)
                                info['is_binary'] = b'\x00' in chunk
                        except Exception:
                            info['is_binary'] = True
                    
                    # Calculate hash for small files
                    if info['size'] < 10 * 1024 * 1024:  # Less than 10MB
                        try:
                            info['hash_md5'] = self._calculate_file_hash(file_path)
                        except Exception:
                            pass
                            
        except Exception as e:
            logger.warning(f"Error getting file info for {file_path}: {e}")
            
        return info
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

# Global file validator instance
file_validator = FileValidator()

def validate_file_extension(file_path: str, valid_extensions: List[str]) -> bool:
    """Validate file extension using global validator"""
    return file_validator.validate_file_extension(file_path, valid_extensions)

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format with improved precision
    
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
        elif size >= 100:
            return f"{size:.0f} {size_names[i]}"
        elif size >= 10:
            return f"{size:.1f} {size_names[i]}"
        else:
            return f"{size:.2f} {size_names[i]}"
            
    except Exception as e:
        logger.warning(f"Error formatting file size {size_bytes}: {e}")
        return f"{size_bytes} B"

def create_output_directory(directory_path: str, create_parents: bool = True) -> bool:
    """
    Create output directory with enhanced error handling and permissions
    
    Args:
        directory_path: Path to the directory
        create_parents: Whether to create parent directories
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        with PerformanceTimer(f"create_directory_{os.path.basename(directory_path)}"):
            path_obj = Path(directory_path)
            
            if path_obj.exists():
                if path_obj.is_dir():
                    logger.debug(f"Directory already exists: {directory_path}")
                    return True
                else:
                    logger.error(f"Path exists but is not a directory: {directory_path}")
                    return False
            
            path_obj.mkdir(parents=create_parents, exist_ok=True)
            
            # Verify creation and permissions
            if path_obj.exists() and path_obj.is_dir():
                # Test write permissions
                test_file = path_obj / f".test_write_{int(time.time())}"
                try:
                    test_file.touch()
                    test_file.unlink()
                    logger.info(f"Output directory created and verified: {directory_path}")
                    return True
                except Exception as e:
                    logger.error(f"Directory created but not writable: {directory_path} - {e}")
                    return False
            else:
                logger.error(f"Failed to create directory: {directory_path}")
                return False
                
    except PermissionError:
        logger.error(f"Permission denied creating directory: {directory_path}")
        return False
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False

def get_safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Get a safe filename with enhanced character handling and length management
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename string
    """
    try:
        # Characters not allowed in Windows filenames (most restrictive)
        invalid_chars = '<>:"/\\|?*'
        
        # Control characters (0-31)
        control_chars = ''.join(chr(i) for i in range(32))
        
        safe_filename = filename
        
        # Replace invalid characters
        for char in invalid_chars + control_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Replace multiple consecutive underscores with single underscore
        while '__' in safe_filename:
            safe_filename = safe_filename.replace('__', '_')
        
        # Remove leading/trailing spaces, dots, and underscores
        safe_filename = safe_filename.strip(' ._')
        
        # Handle empty filename
        if not safe_filename:
            safe_filename = "converted_file"
        
        # Handle length restriction while preserving extension
        if len(safe_filename) > max_length:
            name, ext = os.path.splitext(safe_filename)
            max_name_length = max_length - len(ext) - 1  # -1 for safety
            if max_name_length > 0:
                safe_filename = name[:max_name_length] + ext
            else:
                safe_filename = name[:max_length]
        
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

def validate_output_directory(directory_path: str) -> Dict[str, Any]:
    """
    Enhanced output directory validation with comprehensive checks
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Dictionary with detailed validation results
    """
    validation = {
        'valid': False,
        'exists': False,
        'writable': False,
        'readable': False,
        'error_message': '',
        'free_space': 0,
        'free_space_formatted': '0 B',
        'absolute_path': '',
        'parent_exists': False,
        'is_network_drive': False
    }
    
    try:
        with PerformanceTimer("validate_output_directory"):
            # Convert to absolute path
            abs_path = os.path.abspath(directory_path)
            validation['absolute_path'] = abs_path
            
            # Check if parent directory exists
            parent_path = os.path.dirname(abs_path)
            validation['parent_exists'] = os.path.exists(parent_path)
            
            # Detect network drives (basic heuristic)
            if platform.system() == "Windows":
                validation['is_network_drive'] = abs_path.startswith('\\\\')
            else:
                validation['is_network_drive'] = '/mnt/' in abs_path or '/media/' in abs_path
            
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
                    validation['free_space_formatted'] = format_file_size(free)
                    
                    # Warn if very low space
                    if free < 100 * 1024 * 1024:  # Less than 100MB
                        validation['error_message'] = f"Very low disk space: {validation['free_space_formatted']}"
                        logger.warning(validation['error_message'])
                else:
                    # Fallback for older Python versions
                    try:
                        statvfs = os.statvfs(abs_path)
                        validation['free_space'] = statvfs.f_bavail * statvfs.f_frsize
                        validation['free_space_formatted'] = format_file_size(validation['free_space'])
                    except AttributeError:
                        validation['free_space'] = -1  # Unknown
                        validation['free_space_formatted'] = "Unknown"
            except Exception as e:
                logger.debug(f"Could not determine free space: {e}")
                validation['free_space'] = -1
                validation['free_space_formatted'] = "Unknown"
            
            validation['valid'] = True
            
    except Exception as e:
        validation['error_message'] = f"Error validating directory: {str(e)}"
        logger.error(f"Directory validation error for {directory_path}: {e}")
    
    return validation

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information for debugging and optimization
    
    Returns:
        Dictionary with detailed system information
    """
    info = {
        'platform': 'unknown',
        'platform_detailed': 'unknown',
        'python_version': 'unknown',
        'python_executable': 'unknown',
        'architecture': 'unknown',
        'machine': 'unknown',
        'processor': 'unknown',
        'cpu_count': 0,
        'memory_total': 0,
        'memory_available': 0,
        'memory_total_formatted': '0 B',
        'memory_available_formatted': '0 B',
        'disk_space_total': 0,
        'disk_space_free': 0,
        'disk_space_total_formatted': '0 B',
        'disk_space_free_formatted': '0 B',
        'temp_directory': '',
        'gui_available': False,
        'environment': {}
    }
    
    try:
        with PerformanceTimer("get_system_info"):
            # Basic platform information
            info['platform'] = platform.system()
            info['platform_detailed'] = platform.platform()
            info['python_version'] = platform.python_version()
            info['python_executable'] = sys.executable
            info['architecture'] = platform.architecture()[0]
            info['machine'] = platform.machine()
            info['processor'] = platform.processor()
            info['cpu_count'] = os.cpu_count() or 0
            
            # Memory information (if psutil is available)
            try:
                import psutil
                memory = psutil.virtual_memory()
                info['memory_total'] = memory.total
                info['memory_available'] = memory.available
                info['memory_total_formatted'] = format_file_size(memory.total)
                info['memory_available_formatted'] = format_file_size(memory.available)
                
                # Disk information
                disk = psutil.disk_usage(os.getcwd())
                info['disk_space_total'] = disk.total
                info['disk_space_free'] = disk.free
                info['disk_space_total_formatted'] = format_file_size(disk.total)
                info['disk_space_free_formatted'] = format_file_size(disk.free)
                
            except ImportError:
                logger.debug("psutil not available for detailed system info")
                
                # Fallback methods
                try:
                    if hasattr(shutil, 'disk_usage'):
                        disk = shutil.disk_usage(os.getcwd())
                        info['disk_space_total'] = disk.total
                        info['disk_space_free'] = disk.free
                        info['disk_space_total_formatted'] = format_file_size(disk.total)
                        info['disk_space_free_formatted'] = format_file_size(disk.free)
                except Exception:
                    pass
            
            # Temporary directory
            info['temp_directory'] = tempfile.gettempdir()
            
            # GUI availability
            try:
                import tkinter
                # Try to create a test Tk instance
                test_root = tkinter.Tk()
                test_root.withdraw()
                test_root.destroy()
                info['gui_available'] = True
            except Exception:
                info['gui_available'] = False
            
            # Relevant environment variables
            env_vars = [
                'PATH', 'PYTHONPATH', 'HOME', 'USER', 'USERNAME', 
                'TEMP', 'TMP', 'DISPLAY', 'SHELL', 'TERM'
            ]
            for var in env_vars:
                if var in os.environ:
                    # Truncate very long environment variables
                    value = os.environ[var]
                    if len(value) > 200:
                        value = value[:197] + "..."
                    info['environment'][var] = value
        
    except Exception as e:
        logger.warning(f"Error collecting system info: {e}")
    
    return info

def check_dependencies() -> Dict[str, Any]:
    """
    Enhanced dependency checking with version compatibility analysis
    
    Returns:
        Dictionary with comprehensive dependency status
    """
    dependencies = {
        'required': {},
        'optional': {},
        'all_satisfied': True,
        'compatibility_issues': [],
        'recommendations': []
    }
    
    try:
        with PerformanceTimer("check_dependencies"):
            # Required dependencies
            required_deps = {
                'tkinter': {'description': 'GUI framework', 'builtin': True},
                'pathlib': {'description': 'Path operations', 'builtin': True},
                'csv': {'description': 'CSV file operations', 'builtin': True},
                'threading': {'description': 'Multi-threading support', 'builtin': True},
                'os': {'description': 'Operating system interface', 'builtin': True},
                'sys': {'description': 'System-specific parameters', 'builtin': True}
            }
            
            # Optional dependencies with version requirements
            optional_deps = {
                'asammdf': {
                    'description': 'MDF4 file processing',
                    'min_version': '7.0.0',
                    'recommended_version': '7.4.0'
                },
                'customtkinter': {
                    'description': 'Enhanced GUI components',
                    'min_version': '5.0.0',
                    'recommended_version': '5.2.0'
                },
                'numpy': {
                    'description': 'Numerical computations',
                    'min_version': '1.20.0',
                    'max_version': '1.26.4',  # Avoid 2.x
                    'recommended_version': '1.24.0'
                },
                'pandas': {
                    'description': 'Data manipulation',
                    'min_version': '1.5.0',
                    'max_version': '2.2.0',
                    'recommended_version': '2.0.0'
                },
                'psutil': {
                    'description': 'System information',
                    'min_version': '5.8.0',
                    'recommended_version': '5.9.0'
                }
            }
            
            # Check required dependencies
            for dep_name, dep_info in required_deps.items():
                try:
                    module = __import__(dep_name)
                    version = 'built-in' if dep_info.get('builtin') else getattr(module, '__version__', 'unknown')
                    dependencies['required'][dep_name] = {
                        'available': True,
                        'version': version,
                        'description': dep_info['description'],
                        'status': 'ok'
                    }
                except ImportError:
                    dependencies['required'][dep_name] = {
                        'available': False,
                        'version': None,
                        'description': dep_info['description'],
                        'status': 'missing'
                    }
                    dependencies['all_satisfied'] = False
            
            # Check optional dependencies with version analysis
            for dep_name, dep_info in optional_deps.items():
                try:
                    module = __import__(dep_name)
                    version = getattr(module, '__version__', 'unknown')
                    
                    # Analyze version compatibility
                    status = 'ok'
                    issues = []
                    
                    if version != 'unknown':
                        # Check minimum version
                        if 'min_version' in dep_info:
                            if _compare_versions(version, dep_info['min_version']) < 0:
                                status = 'outdated'
                                issues.append(f"Version {version} below minimum {dep_info['min_version']}")
                        
                        # Check maximum version
                        if 'max_version' in dep_info:
                            if _compare_versions(version, dep_info['max_version']) > 0:
                                status = 'incompatible'
                                issues.append(f"Version {version} above maximum {dep_info['max_version']}")
                        
                        # Special case for NumPy 2.x compatibility
                        if dep_name == 'numpy' and version.startswith('2.'):
                            status = 'warning'
                            issues.append("NumPy 2.x may cause compatibility issues with asammdf")
                            dependencies['compatibility_issues'].append(
                                "NumPy 2.x detected - consider downgrading to 1.x for better asammdf compatibility"
                            )
                    
                    dependencies['optional'][dep_name] = {
                        'available': True,
                        'version': version,
                        'description': dep_info['description'],
                        'status': status,
                        'issues': issues,
                        'min_version': dep_info.get('min_version'),
                        'recommended_version': dep_info.get('recommended_version')
                    }
                    
                    # Add recommendations
                    if status in ['outdated', 'incompatible']:
                        rec_version = dep_info.get('recommended_version', dep_info.get('min_version'))
                        dependencies['recommendations'].append(
                            f"Update {dep_name}: pip install {dep_name}>={rec_version}"
                        )
                        
                except ImportError:
                    dependencies['optional'][dep_name] = {
                        'available': False,
                        'version': None,
                        'description': dep_info['description'],
                        'status': 'missing',
                        'issues': [],
                        'min_version': dep_info.get('min_version'),
                        'recommended_version': dep_info.get('recommended_version')
                    }
                    
                    # Add installation recommendation
                    if dep_name in ['asammdf', 'numpy']:  # Critical optional deps
                        rec_version = dep_info.get('recommended_version', dep_info.get('min_version', ''))
                        version_spec = f">={rec_version}" if rec_version else ""
                        dependencies['recommendations'].append(
                            f"Install {dep_name}: pip install {dep_name}{version_spec}"
                        )
    
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        dependencies['error'] = str(e)
    
    return dependencies

def _compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings
    
    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    try:
        # Simple version comparison (works for most cases)
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for v1, v2 in zip(v1_parts, v2_parts):
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
        
        return 0
        
    except Exception:
        # Fallback: string comparison
        if version1 < version2:
            return -1
        elif version1 > version2:
            return 1
        else:
            return 0

def cleanup_temp_files(temp_directory: Optional[str] = None, max_age_hours: int = 24, 
                      pattern: str = "mf4bridge*") -> Dict[str, Any]:
    """
    Enhanced temporary file cleanup with detailed reporting
    
    Args:
        temp_directory: Optional specific directory to clean
        max_age_hours: Maximum age of temp files to keep (in hours)
        pattern: File pattern to match for cleanup
        
    Returns:
        Dictionary with cleanup results
    """
    results = {
        'files_cleaned': 0,
        'bytes_freed': 0,
        'bytes_freed_formatted': '0 B',
        'errors': [],
        'directories_cleaned': 0,
        'duration': 0
    }
    
    try:
        start_time = time.time()
        
        if temp_directory:
            temp_patterns = [os.path.join(temp_directory, pattern)]
        else:
            temp_dir = tempfile.gettempdir()
            temp_patterns = [
                os.path.join(temp_dir, pattern),
                os.path.join(temp_dir, f"{pattern}.tmp"),
                os.path.join(temp_dir, f"tmp_{pattern}")
            ]
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for pattern_path in temp_patterns:
            try:
                matches = glob.glob(pattern_path)
                
                for temp_path in matches:
                    try:
                        # Check file age
                        if os.path.exists(temp_path):
                            file_age = current_time - os.path.getmtime(temp_path)
                            if file_age < max_age_seconds:
                                continue  # Skip recent files
                            
                            # Calculate size before deletion
                            size_freed = 0
                            if os.path.isfile(temp_path):
                                size_freed = os.path.getsize(temp_path)
                                os.remove(temp_path)
                                results['files_cleaned'] += 1
                            elif os.path.isdir(temp_path):
                                # Calculate directory size
                                for dirpath, dirnames, filenames in os.walk(temp_path):
                                    for filename in filenames:
                                        try:
                                            file_path = os.path.join(dirpath, filename)
                                            size_freed += os.path.getsize(file_path)
                                        except Exception:
                                            pass
                                
                                shutil.rmtree(temp_path)
                                results['directories_cleaned'] += 1
                            
                            results['bytes_freed'] += size_freed
                            
                    except Exception as e:
                        error_msg = f"Could not clean {temp_path}: {e}"
                        results['errors'].append(error_msg)
                        logger.debug(error_msg)
                        
            except Exception as e:
                error_msg = f"Error processing pattern {pattern_path}: {e}"
                results['errors'].append(error_msg)
                logger.debug(error_msg)
        
        results['bytes_freed_formatted'] = format_file_size(results['bytes_freed'])
        results['duration'] = time.time() - start_time
        
        if results['files_cleaned'] > 0 or results['directories_cleaned'] > 0:
            logger.info(
                f"Cleanup completed: {results['files_cleaned']} files, "
                f"{results['directories_cleaned']} directories, "
                f"freed {results['bytes_freed_formatted']}"
            )
        
    except Exception as e:
        error_msg = f"Temp file cleanup failed: {e}"
        results['errors'].append(error_msg)
        logger.error(error_msg)
    
    return results

def get_unique_filename(file_path: str, max_attempts: int = 9999) -> str:
    """
    Enhanced unique filename generation with better collision handling
    
    Args:
        file_path: Original file path
        max_attempts: Maximum number of attempts to find unique name
        
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
        
        # Try numbered suffixes first
        for counter in range(1, max_attempts + 1):
            if counter <= 999:
                new_name = f"{stem}_{counter:03d}{suffix}"
            else:
                new_name = f"{stem}_{counter}{suffix}"
            
            new_path = parent / new_name
            
            if not os.path.exists(new_path):
                logger.debug(f"Generated unique filename: {new_path}")
                return str(new_path)
        
        # If all numbered attempts failed, use timestamp + random
        import random
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        unique_name = f"{stem}_{timestamp}_{random_suffix}{suffix}"
        
        return str(parent / unique_name)
        
    except Exception as e:
        logger.error(f"Error generating unique filename for {file_path}: {e}")
        # Fallback: add timestamp
        try:
            timestamp = int(time.time())
            path_obj = Path(file_path)
            fallback_name = f"{path_obj.stem}_{timestamp}{path_obj.suffix}"
            return str(path_obj.parent / fallback_name)
        except:
            return file_path

def get_application_path() -> str:
    """
    Get the path where the application is running from
    
    Returns:
        Application directory path
    """
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle
                app_path = os.path.dirname(sys.executable)
            else:
                # Other packaging tools
                app_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_path = os.path.dirname(os.path.abspath(__file__))
        
        logger.debug(f"Application path detected: {app_path}")
        return app_path
        
    except Exception as e:
        logger.error(f"Error determining application path: {e}")
        return os.getcwd()

def batch_file_operations(file_paths: List[str], operation_func: Callable, max_workers: int = 4) -> List[Any]:
    """
    Perform file operations in parallel with thread pool
    
    Args:
        file_paths: List of file paths to process
        operation_func: Function to apply to each file path
        max_workers: Maximum number of worker threads
        
    Returns:
        List of results from operation_func
    """
    results = []
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(operation_func, path): path 
                for path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {path}: {e}")
                    results.append(None)
                    
    except Exception as e:
        logger.error(f"Error in batch file operations: {e}")
        # Fallback to sequential processing
        for path in file_paths:
            try:
                result = operation_func(path)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {path}: {e}")
                results.append(None)
    
    return results

def create_backup(file_path: str, backup_dir: Optional[str] = None, 
                 keep_backups: int = 5) -> Optional[str]:
    """
    Enhanced backup creation with rotation and verification
    
    Args:
        file_path: Path to file to backup
        backup_dir: Optional backup directory (default: same directory as file)
        keep_backups: Number of backups to keep (rotation)
        
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
        
        # Verify backup
        if os.path.exists(backup_path):
            original_size = os.path.getsize(file_path)
            backup_size = os.path.getsize(backup_path)
            
            if original_size == backup_size:
                logger.info(f"Created verified backup: {backup_path}")
                
                # Cleanup old backups
                _cleanup_old_backups(backup_dir, file_name, keep_backups)
                
                return backup_path
            else:
                logger.error(f"Backup verification failed: size mismatch")
                try:
                    os.remove(backup_path)
                except:
                    pass
                return None
        else:
            logger.error(f"Backup file was not created: {backup_path}")
            return None
        
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return None

def _cleanup_old_backups(backup_dir: str, original_filename: str, keep_count: int):
    """Clean up old backup files, keeping only the most recent ones"""
    try:
        backup_pattern = os.path.join(backup_dir, f"{original_filename}.backup_*")
        backup_files = glob.glob(backup_pattern)
        
        if len(backup_files) > keep_count:
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x))
            
            # Remove oldest backups
            files_to_remove = backup_files[:-keep_count]
            for backup_file in files_to_remove:
                try:
                    os.remove(backup_file)
                    logger.debug(f"Removed old backup: {backup_file}")
                except Exception as e:
                    logger.debug(f"Could not remove old backup {backup_file}: {e}")
                    
    except Exception as e:
        logger.debug(f"Error cleaning up old backups: {e}")

def monitor_system_resources() -> Dict[str, Any]:
    """
    Monitor system resources and return current status
    
    Returns:
        Dictionary with current resource usage
    """
    resources = {
        'timestamp': time.time(),
        'memory_percent': 0.0,
        'memory_available_mb': 0.0,
        'cpu_percent': 0.0,
        'disk_free_mb': 0.0,
        'disk_free_percent': 0.0,
        'load_average': None,
        'warnings': []
    }
    
    try:
        # Try to use psutil for detailed information
        try:
            import psutil
            
            # Memory information
            memory = psutil.virtual_memory()
            resources['memory_percent'] = memory.percent
            resources['memory_available_mb'] = memory.available / (1024 * 1024)
            
            # CPU information
            resources['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            
            # Disk information
            disk = psutil.disk_usage(os.getcwd())
            resources['disk_free_mb'] = disk.free / (1024 * 1024)
            resources['disk_free_percent'] = (disk.free / disk.total) * 100
            
            # Load average (Unix-like systems)
            if hasattr(os, 'getloadavg'):
                resources['load_average'] = os.getloadavg()
            
            # Generate warnings
            if resources['memory_percent'] > 90:
                resources['warnings'].append("High memory usage detected")
            
            if resources['disk_free_percent'] < 10:
                resources['warnings'].append("Low disk space detected")
            
            if resources['cpu_percent'] > 90:
                resources['warnings'].append("High CPU usage detected")
                
        except ImportError:
            # Fallback without psutil
            try:
                # Basic disk space check
                if hasattr(shutil, 'disk_usage'):
                    disk = shutil.disk_usage(os.getcwd())
                    resources['disk_free_mb'] = disk.free / (1024 * 1024)
                    resources['disk_free_percent'] = (disk.free / disk.total) * 100
                    
                    if resources['disk_free_percent'] < 10:
                        resources['warnings'].append("Low disk space detected")
            except Exception:
                pass
        
    except Exception as e:
        logger.debug(f"Error monitoring system resources: {e}")
        resources['error'] = str(e)
    
    return resources

class ProgressReporter:
    """Enhanced progress reporting with estimated time remaining"""
    
    def __init__(self, total_items: int, update_callback: Optional[Callable] = None):
        self.total_items = total_items
        self.update_callback = update_callback
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.processed_items = 0
        self.last_percentage = 0
        
    def update(self, processed_items: int, message: str = ""):
        """Update progress with ETA calculation"""
        self.processed_items = processed_items
        current_time = time.time()
        
        # Calculate percentage
        percentage = (processed_items / self.total_items) * 100 if self.total_items > 0 else 0
        
        # Only update if significant change or enough time passed
        time_since_update = current_time - self.last_update_time
        percentage_change = abs(percentage - self.last_percentage)
        
        if percentage_change >= 1.0 or time_since_update >= 2.0 or processed_items >= self.total_items:
            # Calculate ETA
            elapsed_time = current_time - self.start_time
            if processed_items > 0 and elapsed_time > 0:
                rate = processed_items / elapsed_time
                remaining_items = self.total_items - processed_items
                eta_seconds = remaining_items / rate if rate > 0 else 0
                
                # Format ETA
                if eta_seconds > 3600:
                    eta_str = f"{eta_seconds/3600:.1f}h"
                elif eta_seconds > 60:
                    eta_str = f"{eta_seconds/60:.1f}m"
                else:
                    eta_str = f"{eta_seconds:.0f}s"
                
                enhanced_message = f"{message} (ETA: {eta_str})" if message else f"ETA: {eta_str}"
            else:
                enhanced_message = message
            
            # Call update callback
            if self.update_callback:
                self.update_callback(enhanced_message, percentage)
            
            self.last_update_time = current_time
            self.last_percentage = percentage

def create_performance_report(start_time: float, end_time: float, 
                            stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a comprehensive performance report
    
    Args:
        start_time: Operation start time
        end_time: Operation end time
        stats: Statistics dictionary
        
    Returns:
        Performance report dictionary
    """
    report = {
        'duration_seconds': end_time - start_time,
        'duration_formatted': '',
        'throughput': {},
        'resource_usage': {},
        'efficiency_metrics': {},
        'recommendations': []
    }
    
    try:
        duration = report['duration_seconds']
        
        # Format duration
        if duration > 3600:
            report['duration_formatted'] = f"{duration/3600:.2f} hours"
        elif duration > 60:
            report['duration_formatted'] = f"{duration/60:.2f} minutes"
        else:
            report['duration_formatted'] = f"{duration:.2f} seconds"
        
        # Calculate throughput metrics
        if 'total_messages' in stats and duration > 0:
            messages_per_second = stats['total_messages'] / duration
            report['throughput']['messages_per_second'] = messages_per_second
            report['throughput']['messages_per_minute'] = messages_per_second * 60
        
        if 'total_files' in stats and duration > 0:
            files_per_minute = (stats['total_files'] / duration) * 60
            report['throughput']['files_per_minute'] = files_per_minute
        
        if 'total_output_size' in stats and duration > 0:
            mb_per_second = (stats['total_output_size'] / (1024 * 1024)) / duration
            report['throughput']['mb_per_second'] = mb_per_second
        
        # Resource usage metrics
        if 'peak_memory_mb' in stats:
            report['resource_usage']['peak_memory_mb'] = stats['peak_memory_mb']
            
            # Memory efficiency recommendations
            if stats['peak_memory_mb'] > 1000:
                report['recommendations'].append("Consider reducing chunk size for lower memory usage")
            elif stats['peak_memory_mb'] < 100:
                report['recommendations'].append("Could increase chunk size for better performance")
        
        # Efficiency metrics
        if 'successful_conversions' in stats and 'total_conversions' in stats:
            success_rate = (stats['successful_conversions'] / stats['total_conversions']) * 100
            report['efficiency_metrics']['success_rate_percent'] = success_rate
            
            if success_rate < 90:
                report['recommendations'].append("Low success rate - check input file quality")
        
        # Performance recommendations
        if duration > 300:  # More than 5 minutes
            report['recommendations'].append("Long conversion time - consider processing smaller batches")
        
        if report['throughput'].get('messages_per_second', 0) < 1000:
            report['recommendations'].append("Low throughput - check system resources and file optimization")
        
    except Exception as e:
        logger.error(f"Error creating performance report: {e}")
        report['error'] = str(e)
    
    return report