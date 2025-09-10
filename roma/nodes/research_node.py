"""
Research Node - Performs deep research queries on analyzed content.
"""

from typing import Optional, List, Dict, Any
from .base_node import BaseNode, NodeState
from ..tools.research_tools import ResearchTool, ResearchQuery, ResearchFinding


class ResearchNode(BaseNode):
    """Node responsible for executing research queries on analyzed content."""
    
    def __init__(self):
        super().__init__("ResearchNode")
        self.research_tool = ResearchTool()
    
    def validate_input(self, state: NodeState) -> Optional[str]:
        """Validate that we have analyzed content and a research query."""
        if not state.analyzed_content:
            return "No analyzed content available for research"
        
        if not state.query and not state.query_keywords:
            return "No research query or keywords specified"
        
        return None
    
    async def process(self, state: NodeState) -> NodeState:
        """
        Execute research queries on analyzed content.
        
        Args:
            state: Current workflow state with analyzed_content and query parameters
            
        Returns:
            Updated state with research_findings
        """
        self.logger.info("Starting research query execution")
        
        # Prepare research query
        research_query = self._prepare_research_query(state)
        
        self.logger.info(f"Research query: '{research_query.query}'")
        self.logger.info(f"Keywords: {research_query.keywords}")
        self.logger.info(f"Depth: {research_query.depth}")
        self.logger.info(f"Max results: {research_query.max_results}")
        
        # Execute research query
        findings = self.research_tool.research_query(research_query, state.analyzed_content)
        
        self.logger.info(f"Found {len(findings)} research findings")
        
        # Convert findings to serializable format
        serializable_findings = []
        for finding in findings:
            serializable_finding = {
                "content": finding.content,
                "source_file": finding.source_file,
                "confidence": finding.confidence,
                "category": finding.category,
                "keywords": finding.keywords,
                "context": finding.context,
                "metadata": finding.metadata
            }
            serializable_findings.append(serializable_finding)
        
        state.research_findings = serializable_findings
        
        # Generate research statistics
        research_stats = self._generate_research_statistics(findings, research_query)
        
        # Add research statistics to metadata
        state.metadata = getattr(state, 'metadata', {})
        state.metadata['research_stats'] = research_stats
        
        # Log research results summary
        self._log_research_summary(research_stats)
        
        return state
    
    def _prepare_research_query(self, state: NodeState) -> ResearchQuery:
        """Prepare research query from state parameters."""
        # Use explicit query or construct from keywords
        query_text = state.query or " ".join(state.query_keywords or [])
        
        # Prepare keywords
        keywords = state.query_keywords or []
        if state.query and not keywords:
            # Extract basic keywords from query
            keywords = [word.lower().strip() for word in state.query.split() if len(word) > 2]
        
        # Prepare file patterns
        file_patterns = state.file_patterns or []
        
        # Determine categories based on keywords
        categories = self._infer_categories(keywords)
        
        return ResearchQuery(
            query=query_text,
            keywords=keywords,
            categories=categories,
            file_patterns=file_patterns,
            depth=state.research_depth,
            max_results=state.max_results
        )
    
    def _infer_categories(self, keywords: List[str]) -> List[str]:
        """Infer research categories from keywords."""
        category_keywords = {
            "technical": ["code", "programming", "software", "api", "algorithm", "function", "class", "method"],
            "business": ["revenue", "profit", "market", "customer", "strategy", "business", "sales", "growth"],
            "research": ["study", "analysis", "research", "findings", "results", "data", "experiment", "hypothesis"],
            "documentation": ["manual", "guide", "tutorial", "documentation", "instructions", "readme", "wiki"],
            "legal": ["law", "legal", "regulation", "compliance", "contract", "terms", "policy", "license"],
            "scientific": ["theory", "science", "scientific", "measurement", "observation", "conclusion", "method"]
        }
        
        inferred_categories = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for category, cat_keywords in category_keywords.items():
            if any(cat_kw in keywords_lower for cat_kw in cat_keywords):
                inferred_categories.append(category)
        
        return inferred_categories if inferred_categories else ["general"]
    
    def _generate_research_statistics(self, findings: List[ResearchFinding], query: ResearchQuery) -> Dict[str, Any]:
        """Generate statistics about research results."""
        if not findings:
            return {
                "total_findings": 0,
                "query": query.query,
                "keywords_searched": query.keywords
            }
        
        # Basic statistics
        total_findings = len(findings)
        avg_confidence = sum(f.confidence for f in findings) / total_findings
        
        # Findings by category
        category_counts = {}
        for finding in findings:
            category = finding.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Findings by source file
        source_file_counts = {}
        for finding in findings:
            source_file = finding.source_file
            source_file_counts[source_file] = source_file_counts.get(source_file, 0) + 1
        
        # Top source files
        top_source_files = sorted(source_file_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Confidence distribution
        high_confidence = len([f for f in findings if f.confidence >= 0.7])
        medium_confidence = len([f for f in findings if 0.4 <= f.confidence < 0.7])
        low_confidence = len([f for f in findings if f.confidence < 0.4])
        
        # Most common keywords in findings
        all_finding_keywords = []
        for finding in findings:
            all_finding_keywords.extend(finding.keywords)
        
        keyword_counts = {}
        for keyword in all_finding_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_findings": total_findings,
            "avg_confidence": avg_confidence,
            "query": query.query,
            "keywords_searched": query.keywords,
            "categories_found": list(category_counts.keys()),
            "category_distribution": category_counts,
            "top_source_files": top_source_files,
            "confidence_distribution": {
                "high": high_confidence,
                "medium": medium_confidence,
                "low": low_confidence
            },
            "top_keywords_in_findings": top_keywords,
            "unique_source_files": len(source_file_counts)
        }
    
    def _log_research_summary(self, research_stats: Dict[str, Any]):
        """Log a summary of research results."""
        total = research_stats.get("total_findings", 0)
        avg_conf = research_stats.get("avg_confidence", 0)
        categories = research_stats.get("categories_found", [])
        unique_files = research_stats.get("unique_source_files", 0)
        
        self.logger.info(f"Research Summary:")
        self.logger.info(f"  - Total findings: {total}")
        self.logger.info(f"  - Average confidence: {avg_conf:.2f}")
        self.logger.info(f"  - Categories found: {', '.join(categories)}")
        self.logger.info(f"  - Unique source files: {unique_files}")
        
        # Log confidence distribution
        conf_dist = research_stats.get("confidence_distribution", {})
        self.logger.info(f"  - High confidence: {conf_dist.get('high', 0)}")
        self.logger.info(f"  - Medium confidence: {conf_dist.get('medium', 0)}")
        self.logger.info(f"  - Low confidence: {conf_dist.get('low', 0)}")
    
    def validate_output(self, state: NodeState) -> Optional[str]:
        """Validate research results."""
        if not state.research_findings:
            return "No research findings were generated"
        
        research_stats = state.metadata.get('research_stats', {})
        total_findings = research_stats.get('total_findings', 0)
        avg_confidence = research_stats.get('avg_confidence', 0)
        
        if total_findings == 0:
            return "Research statistics indicate no findings were generated"
        
        if avg_confidence < 0.2:
            return f"Very low average confidence in findings ({avg_confidence:.2f}). Consider refining the query."
        
        return None