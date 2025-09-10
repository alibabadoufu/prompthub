"""
Simplified demo of Deep Research functionality without external dependencies.
This demonstrates the core file analysis capabilities.
"""

import os
import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional


class SimpleFileAnalyzer:
    """Simplified file analyzer without external dependencies."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
    
    def list_files(self, pattern: str = "*", recursive: bool = True) -> List[str]:
        """List files matching a pattern."""
        if recursive:
            pattern = f"**/{pattern}"
        
        files = []
        try:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.workspace_path)
                    files.append(str(rel_path))
        except Exception as e:
            print(f"Error listing files: {e}")
        
        return sorted(files)
    
    def search_files(self, query: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Search for query in files."""
        results = []
        
        if file_types is None:
            file_types = ["py", "js", "ts", "md", "txt", "json", "yaml", "yml"]
        
        # Get files to search
        files_to_search = []
        for ext in file_types:
            files_to_search.extend(self.list_files(f"*.{ext}"))
        
        query_lower = query.lower()
        
        for file_path in files_to_search[:50]:  # Limit for performance
            try:
                full_path = self.workspace_path / file_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                if query_lower in content.lower():
                    # Find matching lines
                    lines = content.split('\n')
                    matching_lines = []
                    
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            matching_lines.append({
                                "line_number": i + 1,
                                "content": line.strip(),
                                "context": self._get_context(lines, i, 2)
                            })
                    
                    if matching_lines:
                        results.append({
                            "file": file_path,
                            "matches": len(matching_lines),
                            "matching_lines": matching_lines[:5],  # Top 5 matches
                            "file_size": len(content),
                            "relevance_score": self._calculate_relevance(query, content)
                        })
                        
            except Exception as e:
                continue  # Skip files we can't read
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results
    
    def _get_context(self, lines: List[str], center_line: int, context_size: int) -> List[str]:
        """Get context around a line."""
        start = max(0, center_line - context_size)
        end = min(len(lines), center_line + context_size + 1)
        return lines[start:end]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate simple relevance score."""
        query_words = query.lower().split()
        content_lower = content.lower()
        
        matches = sum(1 for word in query_words if word in content_lower)
        return matches / len(query_words) if query_words else 0
    
    def analyze_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in search results."""
        analysis = {
            "total_files": len(results),
            "total_matches": sum(r["matches"] for r in results),
            "file_types": Counter(),
            "common_terms": Counter(),
            "insights": []
        }
        
        for result in results:
            # File type analysis
            file_ext = Path(result["file"]).suffix.lower()
            analysis["file_types"][file_ext] += 1
            
            # Extract terms from matching lines
            for match in result["matching_lines"]:
                words = re.findall(r'\b\w+\b', match["content"].lower())
                analysis["common_terms"].update(words)
        
        # Generate insights
        if analysis["total_files"] > 0:
            avg_matches = analysis["total_matches"] / analysis["total_files"]
            analysis["insights"].append(f"Average {avg_matches:.1f} matches per file")
        
        top_file_type = analysis["file_types"].most_common(1)
        if top_file_type:
            ext, count = top_file_type[0]
            analysis["insights"].append(f"Most matches in {ext} files ({count} files)")
        
        top_terms = analysis["common_terms"].most_common(5)
        if top_terms:
            terms = [term for term, count in top_terms if len(term) > 3][:3]
            if terms:
                analysis["insights"].append(f"Common terms: {', '.join(terms)}")
        
        return analysis


def run_simple_demo():
    """Run simplified demo."""
    print("🚀 Simple Deep Research Demo")
    print("=" * 50)
    print("This demo shows core file analysis without external dependencies")
    
    workspace_path = "/workspace"
    analyzer = SimpleFileAnalyzer(workspace_path)
    
    # Demo queries
    demo_queries = [
        "gradio",
        "database",
        "config",
        "import",
        "function"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*40}")
        print(f"🔍 Query {i}: '{query}'")
        print(f"{'='*40}")
        
        # Search files
        results = analyzer.search_files(query)
        
        print(f"📊 Found {len(results)} files with matches")
        
        if results:
            # Show top results
            print(f"\n🎯 Top Results:")
            for j, result in enumerate(results[:3], 1):
                print(f"  {j}. {result['file']} ({result['matches']} matches, "
                      f"score: {result['relevance_score']:.2f})")
                
                # Show a sample match
                if result['matching_lines']:
                    sample_match = result['matching_lines'][0]
                    print(f"     Line {sample_match['line_number']}: "
                          f"{sample_match['content'][:80]}...")
            
            # Analyze patterns
            analysis = analyzer.analyze_patterns(results)
            
            print(f"\n💡 Analysis:")
            print(f"  - Total matches: {analysis['total_matches']}")
            print(f"  - File types: {dict(analysis['file_types'])}")
            
            for insight in analysis['insights']:
                print(f"  - {insight}")
        else:
            print("  No matches found")
    
    print(f"\n🎉 Simple demo completed!")
    print("To run the full system with advanced features:")
    print("  1. Install dependencies: python3 install_deep_research.py")
    print("  2. Run full demo: python3 deep_research_demo.py")
    print("  3. Interactive mode: python3 -m deep_research.main --interactive --workspace /workspace")


def interactive_simple_demo():
    """Interactive simple demo."""
    print("🎯 Interactive Simple Research Demo")
    print("Type your search queries (or 'quit' to exit)")
    
    workspace_path = "/workspace"
    analyzer = SimpleFileAnalyzer(workspace_path)
    
    while True:
        try:
            query = input("\n🔍 Search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Demo finished!")
                break
            
            if not query:
                continue
            
            print(f"\n🚀 Searching for: '{query}'")
            results = analyzer.search_files(query)
            
            print(f"📊 Found {len(results)} files with matches")
            
            if results:
                # Show top 3 results
                for i, result in enumerate(results[:3], 1):
                    print(f"\n{i}. {result['file']} (Score: {result['relevance_score']:.2f})")
                    print(f"   Matches: {result['matches']}")
                    
                    # Show first match
                    if result['matching_lines']:
                        match = result['matching_lines'][0]
                        print(f"   Line {match['line_number']}: {match['content'][:100]}...")
                
                # Quick analysis
                analysis = analyzer.analyze_patterns(results)
                if analysis['insights']:
                    print(f"\n💡 Quick insight: {analysis['insights'][0]}")
            else:
                print("❌ No matches found. Try a different query.")
                
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_simple_demo()
    else:
        run_simple_demo()