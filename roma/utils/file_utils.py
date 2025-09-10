"""
File utility functions for the ROMA research agent.
"""

import os
import re
from pathlib import Path
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        Path object for the directory
    """
    directory_path = Path(directory_path)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def clean_filename(filename: str, replacement: str = "_") -> str:
    """
    Clean a filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid characters with
        
    Returns:
        Cleaned filename
    """
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, replacement, filename)
    
    # Remove leading/trailing whitespace and dots
    cleaned = cleaned.strip(' .')
    
    # Ensure filename is not empty
    if not cleaned:
        cleaned = "unnamed_file"
    
    # Limit length
    if len(cleaned) > 255:
        name, ext = os.path.splitext(cleaned)
        max_name_length = 255 - len(ext)
        cleaned = name[:max_name_length] + ext
    
    return cleaned


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        file_path = Path(file_path)
        if file_path.exists() and file_path.is_file():
            size_bytes = file_path.stat().st_size
            return size_bytes / (1024 * 1024)
        return 0.0
    except Exception as e:
        logger.warning(f"Could not get size for {file_path}: {e}")
        return 0.0


def is_text_file(file_path: Union[str, Path], 
                sample_size: int = 8192) -> bool:
    """
    Check if a file is likely to be a text file.
    
    Args:
        file_path: Path to file
        sample_size: Number of bytes to sample
        
    Returns:
        True if file appears to be text
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            return False
        
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        if not sample:
            return True  # Empty file is considered text
        
        # Check for null bytes (common in binary files)
        if b'\x00' in sample:
            return False
        
        # Check for high proportion of printable characters
        try:
            sample.decode('utf-8')
            return True
        except UnicodeDecodeError:
            try:
                sample.decode('latin-1')
                # Check if mostly printable
                printable_chars = sum(1 for byte in sample if 32 <= byte <= 126 or byte in (9, 10, 13))
                return printable_chars / len(sample) > 0.7
            except:
                return False
                
    except Exception as e:
        logger.warning(f"Could not check if {file_path} is text: {e}")
        return False


def safe_filename_from_path(file_path: Union[str, Path]) -> str:
    """
    Create a safe filename from a file path for use in reports.
    
    Args:
        file_path: Original file path
        
    Returns:
        Safe filename string
    """
    file_path = Path(file_path)
    
    # Get relative path if possible
    try:
        # Try to get relative path from current directory
        relative_path = file_path.relative_to(Path.cwd())
        safe_name = str(relative_path)
    except ValueError:
        # Use absolute path
        safe_name = str(file_path)
    
    # Replace path separators with underscores for safety
    safe_name = safe_name.replace(os.sep, '_').replace('/', '_').replace('\\', '_')
    
    return safe_name


def get_relative_path(file_path: Union[str, Path], 
                     base_path: Optional[Union[str, Path]] = None) -> str:
    """
    Get relative path from base path.
    
    Args:
        file_path: File path to make relative
        base_path: Base path (defaults to current directory)
        
    Returns:
        Relative path string
    """
    file_path = Path(file_path)
    base_path = Path(base_path) if base_path else Path.cwd()
    
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        # If relative path can't be computed, return absolute path
        return str(file_path)


def count_lines_in_file(file_path: Union[str, Path]) -> int:
    """
    Count the number of lines in a text file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Number of lines
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            return 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
            
    except Exception as e:
        logger.warning(f"Could not count lines in {file_path}: {e}")
        return 0


def get_file_extension_stats(file_paths: list) -> dict:
    """
    Get statistics about file extensions in a list of paths.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        Dictionary with extension statistics
    """
    extension_counts = {}
    
    for file_path in file_paths:
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        if not extension:
            extension = "(no extension)"
        
        extension_counts[extension] = extension_counts.get(extension, 0) + 1
    
    return extension_counts


def find_files_by_pattern(directory: Union[str, Path], 
                         pattern: str, 
                         recursive: bool = True) -> list:
    """
    Find files matching a glob pattern.
    
    Args:
        directory: Directory to search in
        pattern: Glob pattern
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        return []
    
    try:
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    except Exception as e:
        logger.error(f"Error finding files with pattern {pattern} in {directory}: {e}")
        return []