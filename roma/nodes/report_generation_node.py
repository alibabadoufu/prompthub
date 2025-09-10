"""
Report Generation Node - Generates comprehensive research reports from findings.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from .base_node import BaseNode, NodeState
from ..tools.research_tools import ResearchTool, ResearchQuery, ResearchFinding


class ReportGenerationNode(BaseNode):
    """Node responsible for generating comprehensive research reports."""
    
    def __init__(self):
        super().__init__("ReportGenerationNode")
        self.research_tool = ResearchTool()
    
    def validate_input(self, state: NodeState) -> Optional[str]:
        """Validate that we have research findings."""
        if not state.research_findings:
            return "No research findings available for report generation"
        
        return None
    
    async def process(self, state: NodeState) -> NodeState:
        """
        Generate comprehensive research report.
        
        Args:
            state: Current workflow state with research_findings
            
        Returns:
            Updated state with final_report
        """
        self.logger.info("Generating comprehensive research report")
        
        # Convert research findings back to ResearchFinding objects
        findings = []
        for finding_data in state.research_findings:
            finding = ResearchFinding(
                content=finding_data["content"],
                source_file=finding_data["source_file"],
                confidence=finding_data["confidence"],
                category=finding_data["category"],
                keywords=finding_data["keywords"],
                context=finding_data["context"],
                metadata=finding_data["metadata"]
            )
            findings.append(finding)
        
        # Recreate research query from state
        query = ResearchQuery(
            query=state.query or " ".join(state.query_keywords or []),
            keywords=state.query_keywords or [],
            categories=[],
            file_patterns=state.file_patterns or [],
            depth=state.research_depth,
            max_results=state.max_results
        )
        
        # Generate the main report
        report = self._generate_comprehensive_report(findings, query, state)
        
        state.final_report = report
        
        # Set processing end time
        state.processing_end_time = datetime.now()
        
        self.logger.info("Research report generated successfully")
        self.logger.info(f"Report length: {len(report)} characters")
        
        return state
    
    def _generate_comprehensive_report(self, findings: List[ResearchFinding], 
                                     query: ResearchQuery, state: NodeState) -> str:
        """Generate a comprehensive research report."""
        
        # Get metadata for statistics
        metadata = getattr(state, 'metadata', {})
        file_stats = metadata.get('file_stats', {})
        extraction_stats = metadata.get('extraction_stats', {})
        analysis_stats = metadata.get('analysis_stats', {})
        research_stats = metadata.get('research_stats', {})
        
        # Calculate processing time
        processing_time = "Unknown"
        if state.processing_start_time and state.processing_end_time:
            duration = state.processing_end_time - state.processing_start_time
            processing_time = f"{duration.total_seconds():.2f} seconds"
        elif state.processing_start_time:
            duration = datetime.now() - state.processing_start_time
            processing_time = f"{duration.total_seconds():.2f} seconds (ongoing)"
        
        # Start building the report
        report = "# ROMA Research Agent - Deep Analysis Report\n\n"
        
        # Executive Summary
        report += "## Executive Summary\n\n"
        report += f"This report presents the results of a deep research analysis conducted on local files "
        report += f"using the ROMA (Research-Oriented Multi-Agent) system. The analysis processed "
        report += f"{file_stats.get('total_files', 0)} files and generated {len(findings)} research findings "
        report += f"based on the query: \"{query.query}\".\n\n"
        
        # Query Information
        report += "## Research Query\n\n"
        report += f"**Primary Query:** {query.query}\n"
        report += f"**Keywords:** {', '.join(query.keywords)}\n"
        report += f"**Research Depth:** {query.depth}\n"
        report += f"**Maximum Results:** {query.max_results}\n"
        if query.file_patterns:
            report += f"**File Patterns:** {', '.join(query.file_patterns)}\n"
        report += f"**Processing Time:** {processing_time}\n\n"
        
        # Processing Statistics
        report += "## Processing Statistics\n\n"
        
        # File Discovery Stats
        if file_stats:
            report += "### File Discovery\n"
            report += f"- **Total Files Discovered:** {file_stats.get('total_files', 0)}\n"
            report += f"- **Total Size:** {file_stats.get('total_size', 0) / (1024*1024):.2f} MB\n"
            report += f"- **Supported Files:** {file_stats.get('supported_files', 0)}\n"
            report += f"- **Unsupported Files:** {file_stats.get('unsupported_files', 0)}\n"
            
            # File types breakdown
            by_extension = file_stats.get('by_extension', {})
            if by_extension:
                report += "- **File Types:**\n"
                for ext, count in sorted(by_extension.items(), key=lambda x: x[1], reverse=True)[:10]:
                    report += f"  - {ext}: {count} files\n"
            report += "\n"
        
        # Content Extraction Stats
        if extraction_stats:
            report += "### Content Extraction\n"
            report += f"- **Total Files Processed:** {extraction_stats.get('total_files', 0)}\n"
            report += f"- **Successful Extractions:** {extraction_stats.get('successful_extractions', 0)}\n"
            report += f"- **Failed Extractions:** {extraction_stats.get('failed_extractions', 0)}\n"
            report += f"- **Success Rate:** {extraction_stats.get('success_rate', 0):.1%}\n\n"
        
        # Analysis Stats
        if analysis_stats:
            report += "### Content Analysis\n"
            report += f"- **Files Analyzed:** {analysis_stats.get('total_files_analyzed', 0)}\n"
            report += f"- **Unique Keywords Found:** {analysis_stats.get('total_keywords', 0)}\n"
            report += f"- **Categories Identified:** {analysis_stats.get('total_categories', 0)}\n"
            report += f"- **Average Complexity Score:** {analysis_stats.get('avg_complexity_score', 0):.2f}\n"
            report += f"- **Average Word Count:** {analysis_stats.get('avg_word_count', 0):.0f}\n"
            
            # Content types found
            content_types = analysis_stats.get('content_type_stats', {})
            if any(content_types.values()):
                report += "- **Content Types Found:**\n"
                for content_type, count in content_types.items():
                    if count > 0:
                        report += f"  - {content_type.replace('_', ' ').title()}: {count}\n"
            
            # Most common categories
            common_categories = analysis_stats.get('most_common_categories', [])
            if common_categories:
                report += "- **Most Common Categories:**\n"
                for category, count in common_categories[:5]:
                    report += f"  - {category.title()}: {count} files\n"
            report += "\n"
        
        # Research Results Stats
        if research_stats:
            report += "### Research Results\n"
            report += f"- **Total Findings:** {research_stats.get('total_findings', 0)}\n"
            report += f"- **Average Confidence:** {research_stats.get('avg_confidence', 0):.2f}\n"
            report += f"- **Unique Source Files:** {research_stats.get('unique_source_files', 0)}\n"
            
            conf_dist = research_stats.get('confidence_distribution', {})
            report += f"- **High Confidence Findings:** {conf_dist.get('high', 0)}\n"
            report += f"- **Medium Confidence Findings:** {conf_dist.get('medium', 0)}\n"
            report += f"- **Low Confidence Findings:** {conf_dist.get('low', 0)}\n\n"
        
        # Key Findings Summary
        if findings:
            report += "## Key Findings Summary\n\n"
            
            # Group findings by category
            by_category = {}
            for finding in findings:
                category = finding.category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(finding)
            
            # Top findings by confidence
            top_findings = sorted(findings, key=lambda x: x.confidence, reverse=True)[:5]
            
            report += "### Top 5 Findings (by confidence)\n\n"
            for i, finding in enumerate(top_findings, 1):
                report += f"**{i}. {finding.source_file}** (Confidence: {finding.confidence:.2f})\n"
                report += f"- **Category:** {finding.category}\n"
                report += f"- **Keywords:** {', '.join(finding.keywords[:5])}...\n"
                report += f"- **Context:** {finding.context}\n"
                report += f"- **Content Preview:** {finding.content[:200]}...\n\n"
            
            # Findings by category
            report += "### Findings by Category\n\n"
            for category, category_findings in sorted(by_category.items()):
                report += f"#### {category.title()} ({len(category_findings)} findings)\n\n"
                
                # Show top 3 findings in this category
                top_in_category = sorted(category_findings, key=lambda x: x.confidence, reverse=True)[:3]
                
                for finding in top_in_category:
                    report += f"**Source:** {finding.source_file}\n"
                    report += f"**Confidence:** {finding.confidence:.2f}\n"
                    report += f"**Keywords:** {', '.join(finding.keywords)}\n"
                    report += f"**Content:** {finding.content[:300]}...\n\n"
                    report += "---\n\n"
        
        # Detailed Findings
        if findings:
            report += "## Detailed Findings\n\n"
            
            for i, finding in enumerate(findings, 1):
                report += f"### Finding {i}: {finding.source_file}\n\n"
                report += f"- **Category:** {finding.category}\n"
                report += f"- **Confidence Score:** {finding.confidence:.3f}\n"
                report += f"- **Keywords:** {', '.join(finding.keywords)}\n"
                report += f"- **Context:** {finding.context}\n\n"
                report += "**Content:**\n"
                report += f"```\n{finding.content}\n```\n\n"
                
                # Add metadata if available
                if finding.metadata:
                    report += "**Additional Metadata:**\n"
                    for key, value in finding.metadata.items():
                        if key not in ['query']:  # Skip redundant info
                            report += f"- {key}: {value}\n"
                    report += "\n"
                
                report += "---\n\n"
        
        # Processing Errors and Warnings
        if hasattr(state, 'errors') and state.errors:
            report += "## Processing Errors\n\n"
            for error in state.errors:
                report += f"- **{error.get('node', 'Unknown')}:** {error.get('error', 'Unknown error')}\n"
            report += "\n"
        
        if hasattr(state, 'warnings') and state.warnings:
            report += "## Processing Warnings\n\n"
            for warning in state.warnings:
                report += f"- **{warning.get('node', 'Unknown')}:** {warning.get('warning', 'Unknown warning')}\n"
            report += "\n"
        
        # Node Execution History
        if hasattr(state, 'node_history') and state.node_history:
            report += "## Processing Timeline\n\n"
            for execution in state.node_history:
                status = "✅ Success" if execution.get('success', False) else "❌ Failed"
                report += f"- **{execution.get('node', 'Unknown')}:** {status} "
                report += f"({execution.get('execution_time', 0):.2f}s)\n"
            report += "\n"
        
        # Recommendations
        report += "## Recommendations\n\n"
        report += self._generate_recommendations(findings, research_stats, analysis_stats)
        
        # Footer
        report += "\n---\n\n"
        report += f"*Report generated by ROMA Research Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return report
    
    def _generate_recommendations(self, findings: List[ResearchFinding], 
                                research_stats: Dict[str, Any], 
                                analysis_stats: Dict[str, Any]) -> str:
        """Generate recommendations based on the research results."""
        recommendations = []
        
        # Recommendations based on findings
        if not findings:
            recommendations.append("- No findings were generated. Consider broadening your search terms or checking if the target directory contains relevant content.")
        else:
            avg_confidence = research_stats.get('avg_confidence', 0)
            if avg_confidence < 0.3:
                recommendations.append("- Low average confidence in findings suggests the search terms might not be well-matched to the content. Consider refining your keywords.")
            elif avg_confidence > 0.7:
                recommendations.append("- High confidence findings indicate good keyword matching. Consider expanding the search to discover additional related content.")
        
        # Recommendations based on content analysis
        if analysis_stats:
            total_keywords = analysis_stats.get('total_keywords', 0)
            if total_keywords < 50:
                recommendations.append("- Limited keyword diversity suggests either sparse content or very focused material. Consider analyzing additional files or directories.")
            
            complexity_dist = analysis_stats.get('complexity_distribution', {})
            high_complexity = complexity_dist.get('high', 0)
            total_analyzed = analysis_stats.get('total_files_analyzed', 1)
            
            if high_complexity / total_analyzed > 0.5:
                recommendations.append("- High proportion of complex content detected. Consider using more specific search terms to filter results.")
        
        # Recommendations based on categories
        if research_stats:
            categories = research_stats.get('categories_found', [])
            if len(categories) > 5:
                recommendations.append("- Multiple content categories found. Consider running separate focused searches for each category.")
            elif len(categories) == 1:
                recommendations.append(f"- Content is primarily in the '{categories[0]}' category. Consider expanding search terms to discover related categories.")
        
        # General recommendations
        recommendations.append("- For more targeted results, use specific technical terms or domain-specific keywords.")
        recommendations.append("- Consider adjusting the research depth parameter ('shallow', 'medium', 'deep') based on your needs.")
        recommendations.append("- Use file patterns to focus on specific file types if the results are too broad.")
        
        return "\n".join(recommendations) + "\n"
    
    def validate_output(self, state: NodeState) -> Optional[str]:
        """Validate that a report was generated."""
        if not state.final_report:
            return "No final report was generated"
        
        if len(state.final_report) < 100:
            return "Generated report seems too short"
        
        return None