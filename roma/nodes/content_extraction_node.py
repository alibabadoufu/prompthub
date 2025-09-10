"""
Content Extraction Node - Extracts and parses content from discovered files.
"""

import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from .base_node import BaseNode, NodeState
from ..tools.file_utils import FileHandler
from ..tools.document_parser import DocumentParser


class ContentExtractionNode(BaseNode):
    """Node responsible for extracting content from files."""
    
    def __init__(self, max_concurrent_files: int = 10):
        super().__init__("ContentExtractionNode")
        self.file_handler = FileHandler()
        self.document_parser = DocumentParser()
        self.max_concurrent_files = max_concurrent_files
    
    def validate_input(self, state: NodeState) -> Optional[str]:
        """Validate that we have discovered files."""
        if not state.discovered_files:
            return "No discovered files to extract content from"
        
        return None
    
    async def process(self, state: NodeState) -> NodeState:
        """
        Extract content from discovered files.
        
        Args:
            state: Current workflow state with discovered_files
            
        Returns:
            Updated state with extracted_content
        """
        files = [Path(f) for f in state.discovered_files]
        
        self.logger.info(f"Extracting content from {len(files)} files")
        
        # Process files in batches to avoid overwhelming the system
        extracted_content = []
        batch_size = self.max_concurrent_files
        
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(files)-1)//batch_size + 1}")
            
            batch_results = await self._process_file_batch(batch)
            extracted_content.extend(batch_results)
            
            # Add progress info
            processed_count = min(i + batch_size, len(files))
            self.logger.info(f"Processed {processed_count}/{len(files)} files")
        
        # Filter successful extractions
        successful_extractions = [content for content in extracted_content if content.get("success", False)]
        failed_extractions = [content for content in extracted_content if not content.get("success", False)]
        
        self.logger.info(f"Successfully extracted content from {len(successful_extractions)} files")
        if failed_extractions:
            self.logger.warning(f"Failed to extract content from {len(failed_extractions)} files")
            for failed in failed_extractions[:5]:  # Log first 5 failures
                self.logger.warning(f"Failed: {failed.get('file_path', 'unknown')} - {failed.get('error', 'unknown error')}")
        
        state.extracted_content = successful_extractions
        
        # Add extraction statistics
        state.metadata = getattr(state, 'metadata', {})
        state.metadata['extraction_stats'] = {
            "total_files": len(files),
            "successful_extractions": len(successful_extractions),
            "failed_extractions": len(failed_extractions),
            "success_rate": len(successful_extractions) / len(files) if files else 0
        }
        
        return state
    
    async def _process_file_batch(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Process a batch of files concurrently."""
        tasks = []
        
        for file_path in files:
            task = self._extract_single_file(file_path)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "file_path": str(files[i]),
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _extract_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract content from a single file."""
        try:
            # First try to read as text file
            file_result = await self.file_handler.read_file_async(file_path)
            
            if file_result.get("success", False):
                # For text files, content is directly available
                if file_result.get("file_info", {}).get("category") == "text":
                    return {
                        "file_path": str(file_path),
                        "content": file_result["content"],
                        "file_info": file_result["file_info"],
                        "encoding": file_result.get("encoding"),
                        "extraction_method": "text_reader",
                        "success": True
                    }
            
            # For documents, use document parser
            if file_result.get("file_info", {}).get("category") == "document":
                doc_result = await self.document_parser.parse_document(file_path)
                
                if doc_result.get("success", False):
                    return {
                        "file_path": str(file_path),
                        "content": doc_result["content"],
                        "document_info": doc_result,
                        "file_info": file_result.get("file_info", {}),
                        "extraction_method": "document_parser",
                        "success": True
                    }
                else:
                    return {
                        "file_path": str(file_path),
                        "error": doc_result.get("error", "Document parsing failed"),
                        "file_info": file_result.get("file_info", {}),
                        "success": False
                    }
            
            # If we get here, file reading failed
            return {
                "file_path": str(file_path),
                "error": file_result.get("error", "Content extraction failed"),
                "file_info": file_result.get("file_info", {}),
                "success": False
            }
            
        except Exception as e:
            return {
                "file_path": str(file_path),
                "error": str(e),
                "success": False
            }
    
    def validate_output(self, state: NodeState) -> Optional[str]:
        """Validate content extraction results."""
        if not state.extracted_content:
            return "No content was successfully extracted from any files"
        
        extraction_stats = state.metadata.get('extraction_stats', {})
        success_rate = extraction_stats.get('success_rate', 0)
        
        if success_rate < 0.5:
            return f"Low content extraction success rate: {success_rate:.1%}"
        
        return None