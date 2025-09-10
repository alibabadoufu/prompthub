"""
Content analysis and pattern matching tools for deep research.
"""

import re
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter, defaultdict
from pathlib import Path

from ..models.state import SearchResult


class ContentAnalyzer:
    """Advanced content analysis for research insights."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def analyze_content_patterns(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Analyze patterns across search results."""
        analysis = {
            "common_terms": self._extract_common_terms(results),
            "file_types": self._analyze_file_types(results),
            "content_themes": self._identify_themes(results),
            "code_patterns": self._analyze_code_patterns(results),
            "relationships": self._find_relationships(results),
            "statistics": self._calculate_statistics(results)
        }
        
        return analysis
    
    def extract_key_insights(self, results: List[SearchResult], 
                           min_relevance: float = 0.7) -> List[str]:
        """Extract key insights from search results."""
        insights = []
        high_relevance_results = [r for r in results if r.relevance_score >= min_relevance]
        
        if not high_relevance_results:
            return ["No high-relevance results found"]
        
        # Analyze content themes
        themes = self._identify_themes(high_relevance_results)
        for theme, count in themes.items():
            if count >= 3:  # Theme appears in multiple results
                insights.append(f"Recurring theme: '{theme}' appears in {count} results")
        
        # Analyze file distribution
        file_counter = Counter(r.source for r in high_relevance_results)
        most_relevant_files = file_counter.most_common(3)
        for file_path, count in most_relevant_files:
            insights.append(f"High activity in file: {file_path} ({count} relevant matches)")
        
        # Analyze tools used
        tool_counter = Counter(r.tool_used for r in high_relevance_results)
        for tool, count in tool_counter.items():
            insights.append(f"Tool '{tool}' found {count} relevant results")
        
        return insights
    
    def suggest_follow_up_queries(self, results: List[SearchResult], 
                                 original_query: str) -> List[str]:
        """Suggest follow-up queries based on results."""
        suggestions = []
        
        # Extract common terms not in original query
        common_terms = self._extract_common_terms(results)
        original_terms = set(original_query.lower().split())
        
        new_terms = []
        for term, count in common_terms.items():
            if term not in original_terms and count >= 3:
                new_terms.append(term)
        
        # Generate suggestions
        if new_terms:
            suggestions.append(f"Explore related concepts: {', '.join(new_terms[:5])}")
        
        # File-specific suggestions
        file_counter = Counter(r.source for r in results)
        top_files = [f for f, _ in file_counter.most_common(3)]
        if top_files:
            suggestions.append(f"Deep dive into specific files: {', '.join(top_files)}")
        
        # Pattern-based suggestions
        code_patterns = self._analyze_code_patterns(results)
        if code_patterns.get("functions"):
            suggestions.append("Analyze function implementations and relationships")
        if code_patterns.get("classes"):
            suggestions.append("Explore class hierarchies and inheritance patterns")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _extract_common_terms(self, results: List[SearchResult]) -> Dict[str, int]:
        """Extract common terms from results."""
        all_text = " ".join(r.content for r in results)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        return dict(Counter(filtered_words).most_common(20))
    
    def _analyze_file_types(self, results: List[SearchResult]) -> Dict[str, int]:
        """Analyze distribution of file types in results."""
        file_types = []
        for result in results:
            if '.' in result.source:
                ext = result.source.split('.')[-1].lower()
                file_types.append(ext)
        
        return dict(Counter(file_types))
    
    def _identify_themes(self, results: List[SearchResult]) -> Dict[str, int]:
        """Identify content themes using keyword clustering."""
        # Define theme keywords
        theme_keywords = {
            "data_processing": ["data", "process", "transform", "parse", "convert"],
            "api_integration": ["api", "request", "response", "endpoint", "http"],
            "database": ["database", "query", "table", "sql", "model"],
            "authentication": ["auth", "login", "token", "user", "password"],
            "configuration": ["config", "setting", "parameter", "option", "environment"],
            "error_handling": ["error", "exception", "try", "catch", "handle"],
            "testing": ["test", "mock", "assert", "spec", "unit"],
            "logging": ["log", "debug", "info", "warn", "error"],
            "performance": ["performance", "optimize", "cache", "speed", "memory"],
            "security": ["security", "encrypt", "decrypt", "hash", "secure"]
        }
        
        theme_counts = defaultdict(int)
        
        for result in results:
            content_lower = result.content.lower()
            for theme, keywords in theme_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in content_lower)
                if matches >= 2:  # At least 2 keywords match
                    theme_counts[theme] += 1
        
        return dict(theme_counts)
    
    def _analyze_code_patterns(self, results: List[SearchResult]) -> Dict[str, List[str]]:
        """Analyze code patterns in results."""
        patterns = {
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "constants": []
        }
        
        for result in results:
            content = result.content
            
            # Function patterns
            func_matches = re.findall(r'def\s+(\w+)\s*\(|function\s+(\w+)\s*\(', content)
            patterns["functions"].extend([m[0] or m[1] for m in func_matches])
            
            # Class patterns
            class_matches = re.findall(r'class\s+(\w+)', content)
            patterns["classes"].extend(class_matches)
            
            # Import patterns
            import_matches = re.findall(r'(?:import|from)\s+(\w+)', content)
            patterns["imports"].extend(import_matches)
            
            # Variable patterns (simple heuristic)
            var_matches = re.findall(r'(\w+)\s*=\s*["\'\d\[]', content)
            patterns["variables"].extend(var_matches)
            
            # Constant patterns (uppercase variables)
            const_matches = re.findall(r'([A-Z][A-Z_]+)\s*=', content)
            patterns["constants"].extend(const_matches)
        
        # Remove duplicates and return most common
        for key in patterns:
            patterns[key] = list(dict.fromkeys(patterns[key]))[:10]  # Top 10 unique items
        
        return patterns
    
    def _find_relationships(self, results: List[SearchResult]) -> Dict[str, List[str]]:
        """Find relationships between files and concepts."""
        relationships = {
            "file_connections": [],
            "concept_links": [],
            "dependency_chains": []
        }
        
        # File connections (files that appear together in results)
        file_pairs = defaultdict(int)
        files_in_results = [r.source for r in results]
        file_counter = Counter(files_in_results)
        
        # Find files that commonly appear together
        for i, file1 in enumerate(files_in_results):
            for file2 in files_in_results[i+1:]:
                if file1 != file2:
                    pair = tuple(sorted([file1, file2]))
                    file_pairs[pair] += 1
        
        # Get most connected file pairs
        top_pairs = sorted(file_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
        relationships["file_connections"] = [f"{pair[0]} <-> {pair[1]} ({count})" 
                                          for pair, count in top_pairs]
        
        return relationships
    
    def _calculate_statistics(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Calculate statistics about the results."""
        if not results:
            return {}
        
        relevance_scores = [r.relevance_score for r in results]
        
        return {
            "total_results": len(results),
            "unique_files": len(set(r.source for r in results)),
            "avg_relevance": sum(relevance_scores) / len(relevance_scores),
            "max_relevance": max(relevance_scores),
            "min_relevance": min(relevance_scores),
            "tools_used": list(set(r.tool_used for r in results)),
            "content_length_stats": {
                "avg_length": sum(len(r.content) for r in results) / len(results),
                "max_length": max(len(r.content) for r in results),
                "min_length": min(len(r.content) for r in results)
            }
        }


class PatternMatcher:
    """Advanced pattern matching for specific research needs."""
    
    def __init__(self):
        self.common_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://[^\s<>"{}|\\^`\[\]]+',
            "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            "version": r'\b\d+\.\d+\.\d+\b',
            "uuid": r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
            "hash": r'\b[a-f0-9]{32,64}\b',
            "api_key": r'\b[A-Za-z0-9]{20,}\b',
            "file_path": r'[/\\]?(?:[^/\\:\*\?"<>\|]+[/\\])*[^/\\:\*\?"<>\|]*\.[a-zA-Z0-9]+',
        }
    
    def find_patterns(self, content: str, pattern_types: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Find specific patterns in content."""
        if pattern_types is None:
            pattern_types = list(self.common_patterns.keys())
        
        found_patterns = {}
        
        for pattern_type in pattern_types:
            if pattern_type in self.common_patterns:
                pattern = self.common_patterns[pattern_type]
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_patterns[pattern_type] = list(set(matches))  # Remove duplicates
        
        return found_patterns
    
    def find_custom_pattern(self, content: str, pattern: str, flags: int = 0) -> List[Dict[str, Any]]:
        """Find custom regex pattern with context."""
        matches = []
        
        for match in re.finditer(pattern, content, flags):
            # Get line number and surrounding context
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.end())
            if line_end == -1:
                line_end = len(content)
            
            line_content = content[line_start:line_end]
            line_number = content[:match.start()].count('\n') + 1
            
            matches.append({
                "match": match.group(),
                "start": match.start(),
                "end": match.end(),
                "line_number": line_number,
                "line_content": line_content,
                "context": content[max(0, match.start()-100):match.end()+100]
            })
        
        return matches
    
    def analyze_code_structure(self, content: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code structure patterns."""
        if language.lower() == "python":
            return self._analyze_python_structure(content)
        elif language.lower() in ["javascript", "typescript"]:
            return self._analyze_javascript_structure(content)
        else:
            return self._analyze_generic_structure(content)
    
    def _analyze_python_structure(self, content: str) -> Dict[str, Any]:
        """Analyze Python code structure."""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "decorators": [],
            "docstrings": [],
            "comments": [],
            "complexity_indicators": []
        }
        
        # Functions
        func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        structure["functions"] = [m.group(1) for m in re.finditer(func_pattern, content)]
        
        # Classes
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
        structure["classes"] = [m.group(1) for m in re.finditer(class_pattern, content)]
        
        # Imports
        import_pattern = r'(?:from\s+[\w.]+\s+)?import\s+[\w.,\s*]+'
        structure["imports"] = [m.group() for m in re.finditer(import_pattern, content)]
        
        # Decorators
        decorator_pattern = r'@\w+(?:\([^)]*\))?'
        structure["decorators"] = [m.group() for m in re.finditer(decorator_pattern, content)]
        
        # Docstrings
        docstring_pattern = r'"""[^"]*"""'
        structure["docstrings"] = [m.group() for m in re.finditer(docstring_pattern, content)]
        
        # Comments
        comment_pattern = r'#.*$'
        structure["comments"] = [m.group() for m in re.finditer(comment_pattern, content, re.MULTILINE)]
        
        # Complexity indicators
        if len(structure["functions"]) > 20:
            structure["complexity_indicators"].append("High function count")
        if len(structure["classes"]) > 10:
            structure["complexity_indicators"].append("High class count")
        if content.count("if ") > 15:
            structure["complexity_indicators"].append("High conditional complexity")
        
        return structure
    
    def _analyze_javascript_structure(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code structure."""
        structure = {
            "functions": [],
            "classes": [],
            "imports": [],
            "exports": [],
            "variables": [],
            "complexity_indicators": []
        }
        
        # Functions (various patterns)
        func_patterns = [
            r'function\s+(\w+)\s*\(',
            r'(\w+)\s*:\s*function\s*\(',
            r'(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        ]
        
        for pattern in func_patterns:
            matches = [m.group(1) for m in re.finditer(pattern, content)]
            structure["functions"].extend(matches)
        
        # Classes
        class_pattern = r'class\s+(\w+)'
        structure["classes"] = [m.group(1) for m in re.finditer(class_pattern, content)]
        
        # Imports
        import_pattern = r'import\s+.*?from\s+["\'][^"\']+["\']'
        structure["imports"] = [m.group() for m in re.finditer(import_pattern, content)]
        
        # Exports
        export_pattern = r'export\s+(?:default\s+)?(?:class|function|const|let|var)?\s*\w*'
        structure["exports"] = [m.group() for m in re.finditer(export_pattern, content)]
        
        return structure
    
    def _analyze_generic_structure(self, content: str) -> Dict[str, Any]:
        """Generic code structure analysis."""
        structure = {
            "lines": len(content.split('\n')),
            "words": len(content.split()),
            "characters": len(content),
            "patterns_found": self.find_patterns(content)
        }
        
        return structure