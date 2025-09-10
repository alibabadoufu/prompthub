"""
File Discovery Node - Discovers and filters files for research processing.
"""

import asyncio
from pathlib import Path
from typing import Optional
from .base_node import BaseNode, NodeState
from ..tools.file_utils import FileHandler


class FileDiscoveryNode(BaseNode):
    """Node responsible for discovering files to be processed."""
    
    def __init__(self):
        super().__init__("FileDiscoveryNode")
        self.file_handler = FileHandler()
    
    def validate_input(self, state: NodeState) -> Optional[str]:
        """Validate that we have a directory path."""
        if not state.directory_path:
            return "No directory path specified for file discovery"
        
        directory = Path(state.directory_path)
        if not directory.exists():
            return f"Directory does not exist: {state.directory_path}"
        
        if not directory.is_dir():
            return f"Path is not a directory: {state.directory_path}"
        
        return None
    
    async def process(self, state: NodeState) -> NodeState:
        """
        Discover files in the specified directory.
        
        Args:
            state: Current workflow state with directory_path
            
        Returns:
            Updated state with discovered_files
        """
        directory = Path(state.directory_path)
        
        # Prepare file patterns
        include_patterns = state.file_patterns if state.file_patterns else None
        exclude_patterns = [
            "*.pyc", "*.pyo", "*.pyd", "__pycache__/*", ".git/*", 
            ".svn/*", "node_modules/*", "*.log", "*.tmp", "*.temp",
            ".DS_Store", "Thumbs.db", "*.bak", "*.swp", "*.swo"
        ]
        
        self.logger.info(f"Discovering files in: {directory}")
        if include_patterns:
            self.logger.info(f"Include patterns: {include_patterns}")
        
        # Discover files
        discovered_files = self.file_handler.discover_files(
            directory=directory,
            recursive=True,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        if not discovered_files:
            state.add_warning(f"No supported files found in {directory}", self.name)
            state.discovered_files = []
            return state
        
        # Get file statistics
        file_stats = self.file_handler.get_file_stats(discovered_files)
        
        self.logger.info(f"Discovered {len(discovered_files)} files")
        self.logger.info(f"Total size: {file_stats['total_size'] / (1024*1024):.2f} MB")
        self.logger.info(f"File types: {file_stats['by_extension']}")
        
        # Convert paths to strings for serialization
        state.discovered_files = [str(path) for path in discovered_files]
        
        # Add file statistics to metadata
        if not hasattr(state, 'metadata'):
            state.metadata = {}
        state.metadata = getattr(state, 'metadata', {})
        state.metadata['file_stats'] = file_stats
        
        return state
    
    def validate_output(self, state: NodeState) -> Optional[str]:
        """Validate that files were discovered."""
        if not state.discovered_files:
            return "No files were discovered for processing"
        
        if len(state.discovered_files) > 1000:
            return f"Large number of files discovered ({len(state.discovered_files)}). Consider using more specific file patterns."
        
        return None