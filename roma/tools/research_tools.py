"""
Research tools for content analysis, information extraction, and knowledge discovery.
"""

import re
import logging
from typing import Dict, List, Set, Optional, Tuple, Union, Any
from collections import defaultdict, Counter
from dataclasses import dataclass
from pathlib import Path
import asyncio
import json

from .text_processing import TextProcessor, TextAnalyzer, TextChunk

logger = logging.getLogger(__name__)


@dataclass
class ResearchFinding:
    """Represents a research finding with metadata."""
    content: str
    source_file: str
    confidence: float
    category: str
    keywords: List[str]
    context: str
    metadata: Dict[str, Any]


@dataclass
class ResearchQuery:
    """Represents a research query with parameters."""
    query: str
    keywords: List[str]
    categories: List[str]
    file_patterns: List[str]
    depth: str  # 'shallow', 'medium', 'deep'
    max_results: int


class ContentExtractor:
    """Extracts specific types of content from text."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.text_analyzer = TextAnalyzer()
    
    def extract_code_snippets(self, text: str) -> List[Dict[str, str]]:
        """Extract code snippets from text."""
        snippets = []
        
        # Extract fenced code blocks
        fenced_pattern = r'```(\w+)?\n?(.*?)\n?```'
        fenced_matches = re.findall(fenced_pattern, text, re.DOTALL)
        
        for language, code in fenced_matches:
            snippets.append({
                "type": "fenced",
                "language": language or "unknown",
                "code": code.strip(),
                "context": "code block"
            })
        
        # Extract inline code
        inline_pattern = r'`([^`\n]+)`'
        inline_matches = re.findall(inline_pattern, text)
        
        for code in inline_matches:
            if len(code) > 5:  # Filter out very short inline code
                snippets.append({
                    "type": "inline",
                    "language": "unknown",
                    "code": code,
                    "context": "inline code"
                })
        
        # Extract function definitions (basic patterns)
        function_patterns = [
            r'def\s+(\w+)\s*\([^)]*\):',  # Python
            r'function\s+(\w+)\s*\([^)]*\)\s*{',  # JavaScript
            r'public\s+\w+\s+(\w+)\s*\([^)]*\)\s*{',  # Java
            r'(\w+)\s*\([^)]*\)\s*{',  # C/C++
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                # Extract surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                snippets.append({
                    "type": "function",
                    "language": "inferred",
                    "code": context,
                    "function_name": match.group(1) if match.groups() else "unknown",
                    "context": "function definition"
                })
        
        return snippets
    
    def extract_definitions(self, text: str) -> List[Dict[str, str]]:
        """Extract definitions and explanations from text."""
        definitions = []
        
        # Pattern for definitions
        definition_patterns = [
            r'(\w+(?:\s+\w+)*)\s+is\s+(?:a|an)\s+([^.!?]+[.!?])',
            r'(\w+(?:\s+\w+)*)\s+refers\s+to\s+([^.!?]+[.!?])',
            r'(\w+(?:\s+\w+)*)\s+means\s+([^.!?]+[.!?])',
            r'(\w+(?:\s+\w+)*)\s*:\s+([^.!?]+[.!?])',
            r'Define\s+(\w+(?:\s+\w+)*)\s*:\s*([^.!?]+[.!?])',
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                definitions.append({
                    "term": term,
                    "definition": definition,
                    "context": match.group(0),
                    "type": "explicit_definition"
                })
        
        return definitions
    
    def extract_relationships(self, text: str) -> List[Dict[str, str]]:
        """Extract relationships between entities."""
        relationships = []
        
        # Pattern for relationships
        relationship_patterns = [
            r'(\w+(?:\s+\w+)*)\s+(?:is|are)\s+(?:part\s+of|component\s+of|subset\s+of)\s+(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+(?:depends\s+on|requires|needs)\s+(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+(?:contains|includes|has)\s+(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*)\s+(?:extends|inherits\s+from)\s+(\w+(?:\s+\w+)*)',
        ]
        
        for pattern in relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                object_entity = match.group(2).strip()
                
                # Determine relationship type
                full_match = match.group(0).lower()
                if 'part of' in full_match or 'component of' in full_match:
                    rel_type = 'part_of'
                elif 'depends on' in full_match or 'requires' in full_match:
                    rel_type = 'depends_on'
                elif 'contains' in full_match or 'includes' in full_match:
                    rel_type = 'contains'
                elif 'extends' in full_match or 'inherits' in full_match:
                    rel_type = 'inherits'
                else:
                    rel_type = 'related_to'
                
                relationships.append({
                    "subject": subject,
                    "relationship": rel_type,
                    "object": object_entity,
                    "context": match.group(0)
                })
        
        return relationships
    
    def extract_processes(self, text: str) -> List[Dict[str, Any]]:
        """Extract process descriptions and workflows."""
        processes = []
        
        # Look for numbered steps
        step_pattern = r'(\d+)\.\s+([^.!?]+[.!?])'
        step_matches = re.findall(step_pattern, text)
        
        if len(step_matches) > 1:  # At least 2 steps to be considered a process
            processes.append({
                "type": "numbered_steps",
                "steps": [{"number": int(num), "description": desc.strip()} 
                         for num, desc in step_matches],
                "step_count": len(step_matches)
            })
        
        # Look for bullet points
        bullet_pattern = r'[•\-\*]\s+([^.!?]+[.!?])'
        bullet_matches = re.findall(bullet_pattern, text)
        
        if len(bullet_matches) > 2:
            processes.append({
                "type": "bullet_points",
                "steps": [{"description": desc.strip()} for desc in bullet_matches],
                "step_count": len(bullet_matches)
            })
        
        # Look for workflow keywords
        workflow_keywords = ['first', 'then', 'next', 'finally', 'after', 'before']
        sentences = self.text_processor.tokenize_sentences(text)
        
        workflow_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in workflow_keywords):
                workflow_sentences.append(sentence)
        
        if len(workflow_sentences) > 1:
            processes.append({
                "type": "workflow_description",
                "steps": [{"description": sentence} for sentence in workflow_sentences],
                "step_count": len(workflow_sentences)
            })
        
        return processes


class ResearchTool:
    """Main research tool for analyzing and extracting insights from content."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.text_analyzer = TextAnalyzer()
        self.content_extractor = ContentExtractor()
        
        # Knowledge base for categorizing findings
        self.categories = {
            "technical": ["code", "programming", "software", "algorithm", "api", "database"],
            "business": ["revenue", "profit", "market", "customer", "strategy", "competition"],
            "research": ["study", "analysis", "findings", "results", "methodology", "experiment"],
            "documentation": ["manual", "guide", "tutorial", "instructions", "specification"],
            "legal": ["law", "regulation", "compliance", "contract", "terms", "policy"],
            "scientific": ["theory", "hypothesis", "data", "measurement", "observation", "conclusion"]
        }
    
    def analyze_content(self, content: str, source_file: str = "unknown") -> Dict[str, Any]:
        """
        Perform comprehensive content analysis.
        
        Args:
            content: Text content to analyze
            source_file: Source file path
            
        Returns:
            Dictionary with analysis results
        """
        if not content or not content.strip():
            return {"error": "Empty content", "success": False}
        
        try:
            # Basic text analysis
            text_stats = self.text_analyzer.analyze_text(content)
            
            # Extract various content types
            code_snippets = self.content_extractor.extract_code_snippets(content)
            definitions = self.content_extractor.extract_definitions(content)
            relationships = self.content_extractor.extract_relationships(content)
            processes = self.content_extractor.extract_processes(content)
            
            # Extract keywords and patterns
            keywords = self.text_analyzer.extract_keywords(content)
            patterns = self.text_analyzer.find_patterns(content)
            entities = self.text_analyzer.extract_entities(content)
            
            # Generate summary
            summary = self.text_analyzer.summarize_content(content)
            
            # Categorize content
            categories = self._categorize_content(content, keywords)
            
            # Calculate content complexity
            complexity_score = self._calculate_complexity(text_stats, code_snippets, definitions)
            
            return {
                "source_file": source_file,
                "text_stats": text_stats,
                "summary": summary,
                "keywords": keywords,
                "categories": categories,
                "complexity_score": complexity_score,
                "content_types": {
                    "code_snippets": code_snippets,
                    "definitions": definitions,
                    "relationships": relationships,
                    "processes": processes
                },
                "patterns": patterns,
                "entities": entities,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {"error": str(e), "success": False}
    
    def research_query(self, query: ResearchQuery, content_collection: List[Dict[str, Any]]) -> List[ResearchFinding]:
        """
        Execute a research query against a collection of content.
        
        Args:
            query: Research query parameters
            content_collection: Collection of analyzed content
            
        Returns:
            List of research findings
        """
        findings = []
        query_keywords = [kw.lower() for kw in query.keywords]
        query_text = query.query.lower()
        
        for content_data in content_collection:
            if not content_data.get("success", False):
                continue
            
            source_file = content_data.get("source_file", "unknown")
            
            # Skip if file doesn't match patterns
            if query.file_patterns:
                if not any(pattern in source_file for pattern in query.file_patterns):
                    continue
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance(content_data, query_keywords, query_text)
            
            if relevance_score > 0.1:  # Minimum threshold
                # Extract relevant content sections
                relevant_sections = self._extract_relevant_sections(
                    content_data, query_keywords, query_text, query.depth
                )
                
                for section in relevant_sections:
                    finding = ResearchFinding(
                        content=section["content"],
                        source_file=source_file,
                        confidence=relevance_score,
                        category=self._determine_finding_category(section, query.categories),
                        keywords=section["keywords"],
                        context=section["context"],
                        metadata={
                            "section_type": section["type"],
                            "query": query.query,
                            "relevance_score": relevance_score
                        }
                    )
                    findings.append(finding)
        
        # Sort by confidence and limit results
        findings.sort(key=lambda x: x.confidence, reverse=True)
        return findings[:query.max_results]
    
    def _categorize_content(self, content: str, keywords: List[Tuple[str, float]]) -> List[str]:
        """Categorize content based on keywords and patterns."""
        content_lower = content.lower()
        keyword_texts = [kw[0].lower() for kw in keywords]
        
        detected_categories = []
        
        for category, category_keywords in self.categories.items():
            score = 0
            for cat_keyword in category_keywords:
                if cat_keyword in content_lower:
                    score += 2
                if any(cat_keyword in kw for kw in keyword_texts):
                    score += 1
            
            if score > 2:
                detected_categories.append(category)
        
        return detected_categories if detected_categories else ["general"]
    
    def _calculate_complexity(self, text_stats: Any, code_snippets: List, definitions: List) -> float:
        """Calculate content complexity score."""
        complexity = 0.0
        
        # Base complexity from text stats
        if hasattr(text_stats, 'avg_words_per_sentence'):
            complexity += min(text_stats.avg_words_per_sentence / 20, 1.0) * 0.3
        
        if hasattr(text_stats, 'readability_score'):
            # Lower readability = higher complexity
            complexity += (100 - text_stats.readability_score) / 100 * 0.3
        
        # Code complexity
        if code_snippets:
            complexity += min(len(code_snippets) / 10, 1.0) * 0.2
        
        # Definition complexity
        if definitions:
            complexity += min(len(definitions) / 5, 1.0) * 0.2
        
        return min(complexity, 1.0)
    
    def _calculate_relevance(self, content_data: Dict, query_keywords: List[str], query_text: str) -> float:
        """Calculate relevance score for content against query."""
        score = 0.0
        
        # Check in summary
        summary = content_data.get("summary", "").lower()
        for keyword in query_keywords:
            if keyword in summary:
                score += 0.3
        
        # Check in keywords
        content_keywords = [kw[0].lower() for kw in content_data.get("keywords", [])]
        for keyword in query_keywords:
            if keyword in content_keywords:
                score += 0.2
        
        # Check in categories
        categories = content_data.get("categories", [])
        for keyword in query_keywords:
            if any(keyword in cat for cat in categories):
                score += 0.1
        
        # Check in content types
        content_types = content_data.get("content_types", {})
        for content_type, items in content_types.items():
            for item in items:
                item_text = str(item).lower()
                for keyword in query_keywords:
                    if keyword in item_text:
                        score += 0.1
        
        return min(score, 1.0)
    
    def _extract_relevant_sections(self, content_data: Dict, query_keywords: List[str], 
                                  query_text: str, depth: str) -> List[Dict]:
        """Extract relevant sections from content."""
        sections = []
        
        # Extract from summary
        summary = content_data.get("summary", "")
        if summary and any(keyword in summary.lower() for keyword in query_keywords):
            sections.append({
                "content": summary,
                "type": "summary",
                "keywords": [kw for kw in query_keywords if kw in summary.lower()],
                "context": "Document summary"
            })
        
        # Extract from definitions
        definitions = content_data.get("content_types", {}).get("definitions", [])
        for definition in definitions:
            def_text = f"{definition.get('term', '')}: {definition.get('definition', '')}"
            if any(keyword in def_text.lower() for keyword in query_keywords):
                sections.append({
                    "content": def_text,
                    "type": "definition",
                    "keywords": [kw for kw in query_keywords if kw in def_text.lower()],
                    "context": definition.get("context", "")
                })
        
        # Extract from code snippets if relevant
        code_snippets = content_data.get("content_types", {}).get("code_snippets", [])
        for snippet in code_snippets:
            snippet_text = snippet.get("code", "")
            if any(keyword in snippet_text.lower() for keyword in query_keywords):
                sections.append({
                    "content": snippet_text,
                    "type": "code",
                    "keywords": [kw for kw in query_keywords if kw in snippet_text.lower()],
                    "context": f"{snippet.get('language', 'unknown')} {snippet.get('context', '')}"
                })
        
        # Extract from processes
        processes = content_data.get("content_types", {}).get("processes", [])
        for process in processes:
            process_text = " ".join([step.get("description", "") for step in process.get("steps", [])])
            if any(keyword in process_text.lower() for keyword in query_keywords):
                sections.append({
                    "content": process_text,
                    "type": "process",
                    "keywords": [kw for kw in query_keywords if kw in process_text.lower()],
                    "context": f"{process.get('type', '')} with {process.get('step_count', 0)} steps"
                })
        
        return sections
    
    def _determine_finding_category(self, section: Dict, preferred_categories: List[str]) -> str:
        """Determine the category of a finding."""
        section_type = section.get("type", "")
        
        # Map section types to categories
        type_category_map = {
            "code": "technical",
            "definition": "documentation",
            "process": "documentation",
            "summary": "general"
        }
        
        default_category = type_category_map.get(section_type, "general")
        
        # Check if any preferred categories match
        if preferred_categories:
            for cat in preferred_categories:
                if cat in self.categories:
                    return cat
        
        return default_category
    
    def generate_research_report(self, findings: List[ResearchFinding], query: ResearchQuery) -> str:
        """Generate a comprehensive research report."""
        if not findings:
            return f"No findings for query: '{query.query}'"
        
        report = f"# Research Report\n\n"
        report += f"**Query:** {query.query}\n"
        report += f"**Keywords:** {', '.join(query.keywords)}\n"
        report += f"**Total Findings:** {len(findings)}\n\n"
        
        # Group findings by category
        by_category = defaultdict(list)
        for finding in findings:
            by_category[finding.category].append(finding)
        
        # Summary statistics
        report += "## Summary\n\n"
        report += f"- **Categories Found:** {', '.join(by_category.keys())}\n"
        report += f"- **Source Files:** {len(set(f.source_file for f in findings))}\n"
        report += f"- **Average Confidence:** {sum(f.confidence for f in findings) / len(findings):.2f}\n\n"
        
        # Detailed findings by category
        for category, category_findings in by_category.items():
            report += f"## {category.title()} Findings\n\n"
            
            for i, finding in enumerate(category_findings[:5], 1):  # Limit to top 5 per category
                report += f"### Finding {i}: {finding.source_file}\n"
                report += f"**Confidence:** {finding.confidence:.2f}\n"
                report += f"**Keywords:** {', '.join(finding.keywords)}\n"
                report += f"**Context:** {finding.context}\n\n"
                report += f"```\n{finding.content[:500]}...\n```\n\n"
        
        return report