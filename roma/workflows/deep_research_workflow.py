"""
Deep Research Workflow - Main LangGraph workflow for comprehensive file analysis.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..nodes.base_node import NodeState
from ..nodes.file_discovery_node import FileDiscoveryNode
from ..nodes.content_extraction_node import ContentExtractionNode
from ..nodes.analysis_node import AnalysisNode
from ..nodes.research_node import ResearchNode
from ..nodes.report_generation_node import ReportGenerationNode

logger = logging.getLogger(__name__)


class DeepResearchWorkflow:
    """
    Main workflow class that orchestrates the deep research process using LangGraph.
    
    The workflow follows these steps:
    1. File Discovery - Find relevant files in the target directory
    2. Content Extraction - Extract text content from discovered files
    3. Analysis - Analyze content for patterns, keywords, and insights
    4. Research - Execute specific research queries on analyzed content
    5. Report Generation - Generate comprehensive research reports
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Deep Research Workflow.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize nodes
        self.file_discovery_node = FileDiscoveryNode()
        self.content_extraction_node = ContentExtractionNode(
            max_concurrent_files=self.config.get('max_concurrent_files', 10)
        )
        self.analysis_node = AnalysisNode(
            max_concurrent_analysis=self.config.get('max_concurrent_analysis', 5)
        )
        self.research_node = ResearchNode()
        self.report_generation_node = ReportGenerationNode()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        # Initialize memory saver for checkpointing
        self.memory_saver = MemorySaver()
        
        # Compile the workflow with checkpointing
        self.app = self.workflow.compile(checkpointer=self.memory_saver)
        
        self.logger.info("Deep Research Workflow initialized successfully")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create the state graph
        workflow = StateGraph(NodeState)
        
        # Add nodes to the workflow
        workflow.add_node("file_discovery", self._file_discovery_wrapper)
        workflow.add_node("content_extraction", self._content_extraction_wrapper)
        workflow.add_node("analysis", self._analysis_wrapper)
        workflow.add_node("research", self._research_wrapper)
        workflow.add_node("report_generation", self._report_generation_wrapper)
        
        # Define the workflow edges
        workflow.set_entry_point("file_discovery")
        
        # Add conditional edges based on success/failure
        workflow.add_edge("file_discovery", "content_extraction")
        workflow.add_edge("content_extraction", "analysis")
        workflow.add_edge("analysis", "research")
        workflow.add_edge("research", "report_generation")
        workflow.add_edge("report_generation", END)
        
        return workflow
    
    async def _file_discovery_wrapper(self, state: NodeState) -> NodeState:
        """Wrapper for file discovery node."""
        return await self.file_discovery_node.execute(state)
    
    async def _content_extraction_wrapper(self, state: NodeState) -> NodeState:
        """Wrapper for content extraction node."""
        # Check if previous step had critical errors
        if self._has_critical_errors(state):
            state.add_error("Skipping content extraction due to critical errors in file discovery", "workflow")
            return state
        
        return await self.content_extraction_node.execute(state)
    
    async def _analysis_wrapper(self, state: NodeState) -> NodeState:
        """Wrapper for analysis node."""
        if self._has_critical_errors(state):
            state.add_error("Skipping analysis due to critical errors in previous steps", "workflow")
            return state
        
        return await self.analysis_node.execute(state)
    
    async def _research_wrapper(self, state: NodeState) -> NodeState:
        """Wrapper for research node."""
        if self._has_critical_errors(state):
            state.add_error("Skipping research due to critical errors in previous steps", "workflow")
            return state
        
        return await self.research_node.execute(state)
    
    async def _report_generation_wrapper(self, state: NodeState) -> NodeState:
        """Wrapper for report generation node."""
        if self._has_critical_errors(state):
            state.add_error("Skipping report generation due to critical errors in previous steps", "workflow")
            return state
        
        return await self.report_generation_node.execute(state)
    
    def _has_critical_errors(self, state: NodeState) -> bool:
        """Check if the state has critical errors that should stop the workflow."""
        if not hasattr(state, 'errors') or not state.errors:
            return False
        
        # Consider errors critical if they prevent the next step
        critical_error_indicators = [
            "No discovered files",
            "No extracted content", 
            "No analyzed content",
            "No research findings"
        ]
        
        for error in state.errors:
            error_msg = error.get('error', '').lower()
            if any(indicator.lower() in error_msg for indicator in critical_error_indicators):
                return True
        
        return False
    
    async def run_research(self, 
                          directory_path: str,
                          query: str,
                          query_keywords: Optional[List[str]] = None,
                          file_patterns: Optional[List[str]] = None,
                          research_depth: str = "medium",
                          max_results: int = 50,
                          thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete deep research workflow.
        
        Args:
            directory_path: Path to directory to analyze
            query: Research query string
            query_keywords: Optional list of specific keywords
            file_patterns: Optional file patterns to include
            research_depth: Research depth ('shallow', 'medium', 'deep')
            max_results: Maximum number of results to return
            thread_id: Optional thread ID for checkpointing
            
        Returns:
            Dictionary containing the final results
        """
        
        # Validate inputs
        if not directory_path or not Path(directory_path).exists():
            return {
                "success": False,
                "error": f"Invalid directory path: {directory_path}"
            }
        
        if not query and not query_keywords:
            return {
                "success": False,
                "error": "Either query or query_keywords must be provided"
            }
        
        # Create initial state
        initial_state = NodeState(
            directory_path=directory_path,
            query=query,
            query_keywords=query_keywords or [],
            file_patterns=file_patterns,
            research_depth=research_depth,
            max_results=max_results,
            processing_start_time=datetime.now()
        )
        
        # Generate thread ID if not provided
        if not thread_id:
            thread_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        config = {"configurable": {"thread_id": thread_id}}
        
        self.logger.info(f"Starting deep research workflow with thread_id: {thread_id}")
        self.logger.info(f"Directory: {directory_path}")
        self.logger.info(f"Query: {query}")
        self.logger.info(f"Keywords: {query_keywords}")
        self.logger.info(f"Research depth: {research_depth}")
        
        try:
            # Run the workflow
            final_state = await self.app.ainvoke(initial_state, config=config)
            
            # Extract results
            results = {
                "success": True,
                "thread_id": thread_id,
                "query": query,
                "query_keywords": query_keywords,
                "directory_path": directory_path,
                "processing_time": self._calculate_processing_time(final_state),
                "statistics": {
                    "file_stats": getattr(final_state, 'metadata', {}).get('file_stats', {}),
                    "extraction_stats": getattr(final_state, 'metadata', {}).get('extraction_stats', {}),
                    "analysis_stats": getattr(final_state, 'metadata', {}).get('analysis_stats', {}),
                    "research_stats": getattr(final_state, 'metadata', {}).get('research_stats', {})
                },
                "findings": final_state.research_findings or [],
                "report": final_state.final_report or "No report generated",
                "errors": getattr(final_state, 'errors', []),
                "warnings": getattr(final_state, 'warnings', []),
                "node_history": getattr(final_state, 'node_history', [])
            }
            
            self.logger.info(f"Research workflow completed successfully")
            self.logger.info(f"Generated {len(results['findings'])} findings")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in research workflow: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "thread_id": thread_id
            }
    
    def _calculate_processing_time(self, state: NodeState) -> str:
        """Calculate total processing time."""
        if state.processing_start_time and state.processing_end_time:
            duration = state.processing_end_time - state.processing_start_time
            return f"{duration.total_seconds():.2f} seconds"
        elif state.processing_start_time:
            duration = datetime.now() - state.processing_start_time
            return f"{duration.total_seconds():.2f} seconds"
        else:
            return "Unknown"
    
    async def get_workflow_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a workflow by thread ID.
        
        Args:
            thread_id: Thread ID of the workflow
            
        Returns:
            Current workflow state or None if not found
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = await self.app.aget_state(config)
            
            if state and state.values:
                return {
                    "thread_id": thread_id,
                    "current_state": state.values,
                    "next_steps": state.next,
                    "metadata": state.metadata
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting workflow state for {thread_id}: {e}")
            return None
    
    async def list_workflow_threads(self) -> List[str]:
        """
        List all active workflow threads.
        
        Returns:
            List of thread IDs
        """
        try:
            # This would need to be implemented based on the specific checkpointer
            # For MemorySaver, we'd need to track threads manually
            # For now, return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Error listing workflow threads: {e}")
            return []
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow structure.
        
        Returns:
            Workflow information
        """
        return {
            "name": "Deep Research Workflow",
            "version": "1.0.0",
            "description": "Comprehensive file analysis and research workflow using LangGraph",
            "nodes": [
                self.file_discovery_node.get_node_info(),
                self.content_extraction_node.get_node_info(),
                self.analysis_node.get_node_info(),
                self.research_node.get_node_info(),
                self.report_generation_node.get_node_info()
            ],
            "config": self.config
        }