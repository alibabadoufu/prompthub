#!/usr/bin/env python3
"""
Sample Python code for ROMA Research Agent testing.

This module demonstrates various Python constructs that the research agent
should be able to identify and analyze.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path


# Configuration constants
DEFAULT_CONFIG = {
    "api_endpoint": "https://api.example.com",
    "timeout": 30,
    "max_retries": 3,
    "debug_mode": False
}

# Logger setup
logger = logging.getLogger(__name__)


@dataclass
class DataModel:
    """Sample data model for testing."""
    id: int
    name: str
    description: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Union[str, int]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class DataProcessor:
    """
    Sample data processor class.
    
    This class demonstrates various processing capabilities including:
    - File I/O operations
    - Data validation
    - Error handling
    - Configuration management
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the data processor."""
        self.config = self._load_config(config_path)
        self.processed_items = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return DEFAULT_CONFIG.copy()
    
    def process_file(self, file_path: str) -> Dict[str, Union[str, int, bool]]:
        """
        Process a single file and extract metadata.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary containing file metadata and processing results
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file statistics
        stat = file_path.stat()
        
        # Determine file type
        file_type = self._determine_file_type(file_path)
        
        # Process based on file type
        content_info = self._analyze_content(file_path, file_type)
        
        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "file_type": file_type,
            "last_modified": stat.st_mtime,
            "processing_success": True,
            **content_info
        }
        
        self.processed_items.append(result)
        logger.info(f"Successfully processed {file_path}")
        
        return result
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the type of file based on extension."""
        extension = file_path.suffix.lower()
        
        type_mapping = {
            '.txt': 'text',
            '.md': 'markdown',
            '.py': 'python',
            '.js': 'javascript',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css'
        }
        
        return type_mapping.get(extension, 'unknown')
    
    def _analyze_content(self, file_path: Path, file_type: str) -> Dict:
        """Analyze file content based on type."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "character_count": len(content),
                "line_count": content.count('\n') + 1,
                "word_count": len(content.split()),
                "has_content": bool(content.strip())
            }
            
            # Type-specific analysis
            if file_type == 'python':
                analysis.update(self._analyze_python_code(content))
            elif file_type == 'json':
                analysis.update(self._analyze_json_content(content))
            elif file_type in ['markdown', 'text']:
                analysis.update(self._analyze_text_content(content))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content of {file_path}: {e}")
            return {"analysis_error": str(e)}
    
    def _analyze_python_code(self, content: str) -> Dict:
        """Analyze Python code content."""
        import re
        
        # Count functions and classes
        function_count = len(re.findall(r'def\s+\w+\s*\(', content))
        class_count = len(re.findall(r'class\s+\w+\s*[\(:]', content))
        import_count = len(re.findall(r'^(?:from\s+\w+\s+)?import\s+', content, re.MULTILINE))
        
        return {
            "function_count": function_count,
            "class_count": class_count,
            "import_count": import_count,
            "has_main_block": '__name__ == "__main__"' in content
        }
    
    def _analyze_json_content(self, content: str) -> Dict:
        """Analyze JSON content."""
        try:
            data = json.loads(content)
            return {
                "json_valid": True,
                "json_type": type(data).__name__,
                "json_keys": list(data.keys()) if isinstance(data, dict) else None
            }
        except json.JSONDecodeError:
            return {"json_valid": False}
    
    def _analyze_text_content(self, content: str) -> Dict:
        """Analyze text content."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        return {
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0,
            "has_headings": '#' in content or any(line.isupper() for line in content.split('\n'))
        }
    
    def batch_process(self, file_paths: List[str]) -> List[Dict]:
        """Process multiple files in batch."""
        results = []
        
        for file_path in file_paths:
            try:
                result = self.process_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    "file_path": file_path,
                    "processing_success": False,
                    "error": str(e)
                })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        if not self.processed_items:
            return {"message": "No items processed yet"}
        
        total_items = len(self.processed_items)
        successful_items = sum(1 for item in self.processed_items if item.get("processing_success", False))
        
        file_types = {}
        total_size = 0
        
        for item in self.processed_items:
            if item.get("processing_success", False):
                file_type = item.get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
                total_size += item.get("file_size", 0)
        
        return {
            "total_items": total_items,
            "successful_items": successful_items,
            "success_rate": successful_items / total_items,
            "file_types": file_types,
            "total_size_bytes": total_size,
            "average_file_size": total_size / successful_items if successful_items > 0 else 0
        }


def main():
    """Main function for testing the data processor."""
    processor = DataProcessor()
    
    # Sample file paths (these would be real files in actual usage)
    sample_files = [
        "sample_document.md",
        "sample_code.py",
        "config.json"
    ]
    
    print("Processing sample files...")
    results = processor.batch_process(sample_files)
    
    print(f"Processed {len(results)} files")
    
    # Print statistics
    stats = processor.get_statistics()
    print("\nProcessing Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()