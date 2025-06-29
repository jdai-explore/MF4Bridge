"""
MF4Bridge Utility Functions
Helper functions for file operations and validations
"""

import os
import sys
from pathlib import Path
from typing import List, Union

def validate_file_extension(file_path: str, valid_extensions: List[str]) -> bool:
    """
    Validate if file has a valid extension
    
    Args:
        file_path: Path to the file
        valid_extensions: List of valid extensions (e.g., ['.mf4', '.MF4'])
        
    Returns:
        True if extension is valid, False otherwise
    """
    file_ext = Path(file_path).suffix
    return file_ext in valid_extensions

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
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

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
        return True
    except Exception:
        return False

def get_safe_filename(filename: str) -> str:
    """
    Get a safe filename by removing or replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename string
    """
    # Characters not allowed in Windows filenames
    invalid_chars = '<>:"/\\|?*'
    
    safe_filename = filename
    for char in invalid_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_filename = safe_filename.strip(' .')
    
    # Ensure filename is not empty
    if not safe_filename:
        safe_filename = "converted_file"
    
    return safe_filename

def check_file_permissions(file_path: str) -> dict:
    """
    Check file permissions for read/write access
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with permission status
    """
    permissions = {
        'exists': False,
        'readable': False,
        'writable': False,
        'size': 0
    }
    
    try:
        if os.path.exists(file_path):
            permissions['exists'] = True
            permissions['readable'] = os.access(file_path, os.R_OK)
            permissions['writable'] = os.access(file_path, os.W_OK)
            permissions['size'] = os.path.getsize(file_path)
    except Exception:
        pass  # Keep default False values
    
    return permissions

def get_unique_filename(file_path: str) -> str:
    """
    Get a unique filename by adding a number suffix if file already exists
    
    Args:
        file_path: Original file path
        
    Returns:
        Unique file path
    """
    if not os.path.exists(file_path):
        return file_path
    
    path_obj = Path(file_path)
    stem = path_obj.stem
    suffix = path_obj.suffix
    parent = path_obj.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        
        if not os.path.exists(new_path):
            return str(new_path)
        
        counter += 1
        
        # Prevent infinite loop
        if counter > 999:
            return str(path_obj.with_stem(f"{stem}_{counter}"))

def validate_output_directory(directory_path: str) -> dict:
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
        'error_message': ''
    }
    
    try:
        # Check if directory exists
        if os.path.exists(directory_path):
            validation['exists'] = True
            
            # Check if it's actually a directory
            if not os.path.isdir(directory_path):
                validation['error_message'] = "Path exists but is not a directory"
                return validation
            
            # Check write permissions
            if os.access(directory_path, os.W_OK):
                validation['writable'] = True
                validation['valid'] = True
            else:
                validation['error_message'] = "Directory is not writable"
        else:
            # Try to create directory
            try:
                os.makedirs(directory_path, exist_ok=True)
                validation['exists'] = True
                validation['writable'] = True
                validation['valid'] = True
            except Exception as e:
                validation['error_message'] = f"Cannot create directory: {str(e)}"
                
    except Exception as e:
        validation['error_message'] = f"Error accessing directory: {str(e)}"
    
    return validation

def get_application_path() -> str:
    """
    Get the path where the application is running from
    
    Returns:
        Application directory path
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def log_conversion_result(file_path: str, format_type: str, success: bool, error_msg: str = None):
    """
    Log conversion results to a simple text file
    
    Args:
        file_path: Input file path
        format_type: Output format type
        success: Whether conversion was successful
        error_msg: Error message if conversion failed
    """
    try:
        log_file = os.path.join(get_application_path(), "conversion_log.txt")
        
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "SUCCESS" if success else "FAILED"
            
            log_entry = f"[{timestamp}] {status}: {os.path.basename(file_path)} -> {format_type.upper()}"
            
            if not success and error_msg:
                log_entry += f" - Error: {error_msg}"
            
            f.write(log_entry + "\n")
            
    except Exception:
        # Silently ignore logging errors
        pass

def cleanup_temp_files(temp_directory: str = None):
    """
    Clean up temporary files created during conversion
    
    Args:
        temp_directory: Optional specific directory to clean
    """
    import tempfile
    import glob
    
    try:
        if temp_directory:
            temp_pattern = os.path.join(temp_directory, "mf4bridge_temp_*")
        else:
            temp_pattern = os.path.join(tempfile.gettempdir(), "mf4bridge_temp_*")
        
        temp_files = glob.glob(temp_pattern)
        
        for temp_file in temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                elif os.path.isdir(temp_file):
                    import shutil
                    shutil.rmtree(temp_file)
            except Exception:
                continue  # Skip files that can't be deleted
                
    except Exception:
        pass  # Silently ignore cleanup errors

def get_system_info() -> dict:
    """
    Get basic system information for debugging purposes
    
    Returns:
        Dictionary with system information
    """
    import platform
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture()[0],
        'machine': platform.machine(),
        'processor': platform.processor()
    }