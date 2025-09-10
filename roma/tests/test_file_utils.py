"""
Unit tests for file utilities.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from ..tools.file_utils import FileHandler, FileTypeDetector


class TestFileTypeDetector:
    """Test FileTypeDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = FileTypeDetector()
    
    def test_detect_text_file(self):
        """Test detection of text files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file.")
            temp_path = f.name
        
        try:
            result = self.detector.detect_file_type(temp_path)
            
            assert result["category"] == "text"
            assert result["extension"] == ".txt"
            assert result["supported"] is True
            assert "size" in result
        finally:
            os.unlink(temp_path)
    
    def test_detect_nonexistent_file(self):
        """Test detection of non-existent file."""
        result = self.detector.detect_file_type("/nonexistent/file.txt")
        
        assert "error" in result
        assert result["type"] == "unknown"
    
    def test_supported_extensions(self):
        """Test supported extension checking."""
        assert ".txt" in self.detector.SUPPORTED_TEXT_EXTENSIONS
        assert ".pdf" in self.detector.SUPPORTED_DOCUMENT_EXTENSIONS


class TestFileHandler:
    """Test FileHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = FileHandler()
    
    def test_detect_encoding(self):
        """Test encoding detection."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("Test content with unicode: café")
            temp_path = f.name
        
        try:
            encoding = self.handler.detect_encoding(temp_path)
            assert encoding in ['utf-8', 'UTF-8']
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_read_file_async(self):
        """Test async file reading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_content = "This is test content."
            f.write(test_content)
            temp_path = f.name
        
        try:
            result = await self.handler.read_file_async(temp_path)
            
            assert result["success"] is True
            assert result["content"] == test_content
            assert "file_info" in result
        finally:
            os.unlink(temp_path)
    
    def test_discover_files(self):
        """Test file discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "test1.txt").write_text("Test 1")
            (temp_path / "test2.py").write_text("print('test')")
            (temp_path / "ignore.pyc").write_text("binary")
            
            # Create subdirectory
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()
            (sub_dir / "test3.md").write_text("# Test")
            
            files = self.handler.discover_files(temp_path)
            
            # Should find text files but not .pyc
            file_names = [f.name for f in files]
            assert "test1.txt" in file_names
            assert "test2.py" in file_names
            assert "test3.md" in file_names
            assert "ignore.pyc" not in file_names
    
    def test_get_file_stats(self):
        """Test file statistics generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "test1.txt").write_text("Test content")
            (temp_path / "test2.py").write_text("print('test')")
            
            files = list(temp_path.glob("*"))
            stats = self.handler.get_file_stats(files)
            
            assert stats["total_files"] == 2
            assert stats["total_size"] > 0
            assert ".txt" in stats["by_extension"]
            assert ".py" in stats["by_extension"]