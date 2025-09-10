"""
File utilities for handling various file operations and type detection.
"""

import os
import magic
import chardet
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


class FileTypeDetector:
    """Detects file types and validates file accessibility."""
    
    SUPPORTED_TEXT_EXTENSIONS = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', 
        '.yaml', '.yml', '.csv', '.log', '.rst', '.tex', '.sql', '.sh',
        '.bat', '.ps1', '.c', '.cpp', '.h', '.java', '.php', '.rb', '.go',
        '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.pl', '.lua'
    }
    
    SUPPORTED_DOCUMENT_EXTENSIONS = {
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt'
    }
    
    def __init__(self):
        self.mime = magic.Magic(mime=True)
        
    def detect_file_type(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Detect file type using multiple methods.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file type information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": "File does not exist", "type": "unknown"}
            
        try:
            # Get MIME type
            mime_type = self.mime.from_file(str(file_path))
            
            # Get extension
            extension = file_path.suffix.lower()
            
            # Determine category
            category = self._categorize_file(extension, mime_type)
            
            return {
                "mime_type": mime_type,
                "extension": extension,
                "category": category,
                "size": file_path.stat().st_size,
                "name": file_path.name,
                "supported": self._is_supported(extension, category)
            }
            
        except Exception as e:
            logger.error(f"Error detecting file type for {file_path}: {e}")
            return {"error": str(e), "type": "unknown"}
    
    def _categorize_file(self, extension: str, mime_type: str) -> str:
        """Categorize file based on extension and MIME type."""
        if extension in self.SUPPORTED_TEXT_EXTENSIONS:
            return "text"
        elif extension in self.SUPPORTED_DOCUMENT_EXTENSIONS:
            return "document"
        elif mime_type.startswith("text/"):
            return "text"
        elif mime_type.startswith("application/"):
            if "pdf" in mime_type:
                return "document"
            elif any(doc_type in mime_type for doc_type in ["word", "excel", "powerpoint"]):
                return "document"
            else:
                return "application"
        else:
            return "unknown"
    
    def _is_supported(self, extension: str, category: str) -> bool:
        """Check if file type is supported for processing."""
        return (extension in self.SUPPORTED_TEXT_EXTENSIONS or 
                extension in self.SUPPORTED_DOCUMENT_EXTENSIONS or
                category in ["text", "document"])


class FileHandler:
    """Handles file operations including reading, writing, and batch processing."""
    
    def __init__(self, max_workers: int = 4):
        self.detector = FileTypeDetector()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def detect_encoding(self, file_path: Union[str, Path]) -> str:
        """
        Detect file encoding.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding
        """
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except Exception as e:
            logger.warning(f"Could not detect encoding for {file_path}: {e}")
            return 'utf-8'
    
    async def read_file_async(self, file_path: Union[str, Path]) -> Dict[str, Union[str, Dict]]:
        """
        Asynchronously read a file with proper encoding detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file content and metadata
        """
        file_path = Path(file_path)
        
        # Get file type information
        file_info = self.detector.detect_file_type(file_path)
        
        if not file_info.get("supported", False):
            return {
                "error": f"Unsupported file type: {file_info.get('extension', 'unknown')}",
                "file_info": file_info
            }
        
        try:
            if file_info["category"] == "text":
                encoding = self.detect_encoding(file_path)
                async with aiofiles.open(file_path, 'r', encoding=encoding) as file:
                    content = await file.read()
            else:
                # For documents, we'll handle them in document_parser.py
                content = f"Document file: {file_path.name} (requires document parser)"
            
            return {
                "content": content,
                "file_info": file_info,
                "encoding": encoding if file_info["category"] == "text" else None,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                "error": str(e),
                "file_info": file_info,
                "success": False
            }
    
    def read_file_sync(self, file_path: Union[str, Path]) -> Dict[str, Union[str, Dict]]:
        """
        Synchronously read a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file content and metadata
        """
        return asyncio.run(self.read_file_async(file_path))
    
    async def read_multiple_files(self, file_paths: List[Union[str, Path]]) -> List[Dict]:
        """
        Read multiple files concurrently.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of results for each file
        """
        tasks = [self.read_file_async(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "file_path": str(file_paths[i]),
                    "success": False
                })
            else:
                result["file_path"] = str(file_paths[i])
                processed_results.append(result)
        
        return processed_results
    
    def discover_files(self, directory: Union[str, Path], 
                      recursive: bool = True,
                      include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """
        Discover files in a directory based on patterns.
        
        Args:
            directory: Directory to search
            recursive: Whether to search recursively
            include_patterns: File patterns to include (e.g., ['*.py', '*.txt'])
            exclude_patterns: File patterns to exclude
            
        Returns:
            List of discovered file paths
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            return []
        
        files = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                # Check if file is supported
                file_info = self.detector.detect_file_type(file_path)
                if file_info.get("supported", False):
                    # Apply include/exclude patterns if specified
                    if self._matches_patterns(file_path, include_patterns, exclude_patterns):
                        files.append(file_path)
        
        return sorted(files)
    
    def _matches_patterns(self, file_path: Path, 
                         include_patterns: Optional[List[str]] = None,
                         exclude_patterns: Optional[List[str]] = None) -> bool:
        """Check if file matches include/exclude patterns."""
        import fnmatch
        
        # Check exclude patterns first
        if exclude_patterns:
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(file_path.name, pattern):
                    return False
        
        # Check include patterns
        if include_patterns:
            for pattern in include_patterns:
                if fnmatch.fnmatch(file_path.name, pattern):
                    return True
            return False  # If include patterns specified but no match
        
        return True  # Include by default if no patterns specified
    
    async def write_file_async(self, file_path: Union[str, Path], 
                              content: str, 
                              encoding: str = 'utf-8') -> bool:
        """
        Asynchronously write content to a file.
        
        Args:
            file_path: Path to write to
            content: Content to write
            encoding: File encoding
            
        Returns:
            Success status
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding=encoding) as file:
                await file.write(content)
            
            logger.info(f"Successfully wrote file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    def get_file_stats(self, file_paths: List[Union[str, Path]]) -> Dict[str, int]:
        """
        Get statistics about a collection of files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary with file statistics
        """
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_extension": {},
            "by_category": {},
            "supported_files": 0,
            "unsupported_files": 0
        }
        
        for file_path in file_paths:
            file_info = self.detector.detect_file_type(file_path)
            
            stats["total_files"] += 1
            stats["total_size"] += file_info.get("size", 0)
            
            ext = file_info.get("extension", "unknown")
            category = file_info.get("category", "unknown")
            
            stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            if file_info.get("supported", False):
                stats["supported_files"] += 1
            else:
                stats["unsupported_files"] += 1
        
        return stats
    
    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)