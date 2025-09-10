"""
Analysis Node - Analyzes extracted content for insights and patterns.
"""

import asyncio
from typing import Optional, List, Dict, Any
from .base_node import BaseNode, NodeState
from ..tools.research_tools import ResearchTool


class AnalysisNode(BaseNode):
    """Node responsible for analyzing extracted content."""
    
    def __init__(self, max_concurrent_analysis: int = 5):
        super().__init__("AnalysisNode")
        self.research_tool = ResearchTool()
        self.max_concurrent_analysis = max_concurrent_analysis
    
    def validate_input(self, state: NodeState) -> Optional[str]:
        """Validate that we have extracted content."""
        if not state.extracted_content:
            return "No extracted content to analyze"
        
        return None
    
    async def process(self, state: NodeState) -> NodeState:
        """
        Analyze extracted content.
        
        Args:
            state: Current workflow state with extracted_content
            
        Returns:
            Updated state with analyzed_content
        """
        content_items = state.extracted_content
        
        self.logger.info(f"Analyzing content from {len(content_items)} files")
        
        # Process content in batches to avoid overwhelming the system
        analyzed_content = []
        batch_size = self.max_concurrent_analysis
        
        for i in range(0, len(content_items), batch_size):
            batch = content_items[i:i + batch_size]
            self.logger.info(f"Analyzing batch {i//batch_size + 1}/{(len(content_items)-1)//batch_size + 1}")
            
            batch_results = await self._analyze_content_batch(batch)
            analyzed_content.extend(batch_results)
            
            # Add progress info
            processed_count = min(i + batch_size, len(content_items))
            self.logger.info(f"Analyzed {processed_count}/{len(content_items)} content items")
        
        # Filter successful analyses
        successful_analyses = [analysis for analysis in analyzed_content if analysis.get("success", False)]
        failed_analyses = [analysis for analysis in analyzed_content if not analysis.get("success", False)]
        
        self.logger.info(f"Successfully analyzed {len(successful_analyses)} content items")
        if failed_analyses:
            self.logger.warning(f"Failed to analyze {len(failed_analyses)} content items")
        
        state.analyzed_content = successful_analyses
        
        # Generate analysis statistics
        analysis_stats = self._generate_analysis_statistics(successful_analyses)
        
        # Add analysis statistics to metadata
        state.metadata = getattr(state, 'metadata', {})
        state.metadata['analysis_stats'] = analysis_stats
        
        self.logger.info(f"Analysis complete. Found {analysis_stats['total_keywords']} unique keywords across all content")
        
        return state
    
    async def _analyze_content_batch(self, content_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a batch of content items concurrently."""
        tasks = []
        
        for content_item in content_batch:
            task = self._analyze_single_content(content_item)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "file_path": content_batch[i].get("file_path", "unknown"),
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _analyze_single_content(self, content_item: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single content item."""
        try:
            file_path = content_item.get("file_path", "unknown")
            content = content_item.get("content", "")
            
            if not content or not content.strip():
                return {
                    "file_path": file_path,
                    "error": "Empty content",
                    "success": False
                }
            
            # Run analysis in executor to avoid blocking
            loop = asyncio.get_event_loop()
            analysis_result = await loop.run_in_executor(
                None, 
                self.research_tool.analyze_content, 
                content, 
                file_path
            )
            
            if not analysis_result.get("success", False):
                return {
                    "file_path": file_path,
                    "error": analysis_result.get("error", "Analysis failed"),
                    "success": False
                }
            
            # Add original content metadata
            analysis_result["original_content_info"] = {
                "file_info": content_item.get("file_info", {}),
                "extraction_method": content_item.get("extraction_method", "unknown"),
                "encoding": content_item.get("encoding"),
                "document_info": content_item.get("document_info")
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                "file_path": content_item.get("file_path", "unknown"),
                "error": str(e),
                "success": False
            }
    
    def _generate_analysis_statistics(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive statistics from analyses."""
        if not analyses:
            return {}
        
        # Collect all keywords
        all_keywords = set()
        all_categories = set()
        complexity_scores = []
        word_counts = []
        
        # Content type statistics
        content_type_stats = {
            "code_snippets": 0,
            "definitions": 0,
            "relationships": 0,
            "processes": 0
        }
        
        # File type statistics
        file_extension_stats = {}
        
        for analysis in analyses:
            # Keywords
            keywords = analysis.get("keywords", [])
            all_keywords.update([kw[0] for kw in keywords if isinstance(kw, (list, tuple))])
            
            # Categories
            categories = analysis.get("categories", [])
            all_categories.update(categories)
            
            # Complexity
            complexity = analysis.get("complexity_score", 0)
            complexity_scores.append(complexity)
            
            # Text stats
            text_stats = analysis.get("text_stats")
            if text_stats and hasattr(text_stats, 'word_count'):
                word_counts.append(text_stats.word_count)
            
            # Content types
            content_types = analysis.get("content_types", {})
            for content_type, items in content_types.items():
                if content_type in content_type_stats:
                    content_type_stats[content_type] += len(items) if items else 0
            
            # File extensions
            file_info = analysis.get("original_content_info", {}).get("file_info", {})
            extension = file_info.get("extension", "unknown")
            file_extension_stats[extension] = file_extension_stats.get(extension, 0) + 1
        
        # Calculate averages
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        avg_word_count = sum(word_counts) / len(word_counts) if word_counts else 0
        
        # Find most common categories
        category_counts = {}
        for analysis in analyses:
            for category in analysis.get("categories", []):
                category_counts[category] = category_counts.get(category, 0) + 1
        
        most_common_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_files_analyzed": len(analyses),
            "total_keywords": len(all_keywords),
            "total_categories": len(all_categories),
            "avg_complexity_score": avg_complexity,
            "avg_word_count": avg_word_count,
            "content_type_stats": content_type_stats,
            "file_extension_stats": file_extension_stats,
            "most_common_categories": most_common_categories,
            "complexity_distribution": {
                "low": len([c for c in complexity_scores if c < 0.3]),
                "medium": len([c for c in complexity_scores if 0.3 <= c < 0.7]),
                "high": len([c for c in complexity_scores if c >= 0.7])
            }
        }
    
    def validate_output(self, state: NodeState) -> Optional[str]:
        """Validate analysis results."""
        if not state.analyzed_content:
            return "No content was successfully analyzed"
        
        analysis_stats = state.metadata.get('analysis_stats', {})
        total_analyzed = analysis_stats.get('total_files_analyzed', 0)
        
        if total_analyzed == 0:
            return "Analysis statistics indicate no files were processed"
        
        # Check if we have reasonable keyword extraction
        total_keywords = analysis_stats.get('total_keywords', 0)
        if total_keywords < 10:
            return f"Very few keywords extracted ({total_keywords}). Content might be too sparse or analysis failed"
        
        return None