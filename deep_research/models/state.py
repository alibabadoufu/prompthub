"""
State management for the deep research workflow.
"""

from typing import List, Dict, Any, Optional, TypedDict
from dataclasses import dataclass
from enum import Enum


class ResearchStatus(Enum):
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    ITERATING = "iterating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"


@dataclass
class SearchResult:
    """Represents a single search result from any tool."""
    source: str  # file path or tool name
    content: str
    relevance_score: float
    metadata: Dict[str, Any]
    search_query: str
    tool_used: str


@dataclass
class ResearchIteration:
    """Represents one iteration of research."""
    iteration_number: int
    query: str
    results: List[SearchResult]
    insights: List[str]
    follow_up_questions: List[str]
    status: ResearchStatus


class ResearchState(TypedDict):
    """Main state for the research workflow."""
    # Core research data
    original_query: str
    current_query: str
    research_goal: str
    
    # Research progress
    iterations: List[ResearchIteration]
    current_iteration: int
    status: ResearchStatus
    
    # Search results and findings
    all_results: List[SearchResult]
    key_insights: List[str]
    discovered_files: List[str]
    
    # Research strategy
    search_strategies: List[str]
    completed_searches: List[str]
    pending_searches: List[str]
    
    # Final output
    research_report: Optional[str]
    confidence_score: float
    
    # Configuration
    max_iterations: int
    similarity_threshold: float
    workspace_path: str