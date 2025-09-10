"""
LangGraph nodes for deep research workflow.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.state import ResearchState, SearchResult, ResearchIteration, ResearchStatus
from ..tools.file_tools import FileSearchTool, FileListTool, FileReadTool
from ..tools.retrieval_tools import DenseRetrievalTool, BM25RetrievalTool, HybridRetrievalTool
from ..tools.analysis_tools import ContentAnalyzer, PatternMatcher


class PlanningNode:
    """Node for planning the research strategy."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.file_list_tool = FileListTool(workspace_path)
        
    def __call__(self, state: ResearchState) -> ResearchState:
        """Plan the research strategy."""
        print(f"🔍 Planning research for: {state['original_query']}")
        
        # Discover available files
        all_files = self.file_list_tool.list_files("*", recursive=True)
        code_files = self.file_list_tool.list_by_extension(
            ["py", "js", "ts", "java", "cpp", "c", "h", "css", "html", "json", "yaml", "yml", "md", "txt"]
        )
        
        # Flatten code files
        discovered_files = []
        for file_list in code_files.values():
            discovered_files.extend(file_list)
        
        # Plan search strategies based on query
        query_lower = state['original_query'].lower()
        search_strategies = []
        
        # Basic search strategies
        search_strategies.append("grep_search")
        search_strategies.append("fuzzy_search")
        
        # Advanced strategies based on query content
        if any(term in query_lower for term in ["function", "method", "class", "api"]):
            search_strategies.append("code_structure_analysis")
            
        if any(term in query_lower for term in ["config", "setting", "parameter"]):
            search_strategies.append("config_file_search")
            
        if any(term in query_lower for term in ["data", "process", "transform"]):
            search_strategies.append("data_flow_analysis")
            
        # Add retrieval strategies for complex queries
        if len(state['original_query'].split()) > 3:
            search_strategies.extend(["dense_retrieval", "bm25_retrieval", "hybrid_retrieval"])
        
        # Update state
        state['discovered_files'] = discovered_files[:100]  # Limit for performance
        state['search_strategies'] = search_strategies
        state['pending_searches'] = search_strategies.copy()
        state['status'] = ResearchStatus.SEARCHING
        state['current_iteration'] = 0
        
        print(f"📁 Discovered {len(discovered_files)} files")
        print(f"🎯 Planned {len(search_strategies)} search strategies")
        
        return state


class SearchNode:
    """Node for executing search operations."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.file_search_tool = FileSearchTool(workspace_path)
        self.file_list_tool = FileListTool(workspace_path)
        self.file_read_tool = FileReadTool(workspace_path)
        self.pattern_matcher = PatternMatcher()
        
        # Initialize retrieval tools (will be indexed on first use)
        self.dense_tool = None
        self.bm25_tool = None
        self.hybrid_tool = None
        
    def __call__(self, state: ResearchState) -> ResearchState:
        """Execute search operations."""
        if not state['pending_searches']:
            state['status'] = ResearchStatus.ANALYZING
            return state
        
        current_query = state['current_query'] or state['original_query']
        print(f"🔎 Searching for: {current_query}")
        
        # Get next search strategy
        strategy = state['pending_searches'][0]
        state['pending_searches'] = state['pending_searches'][1:]
        state['completed_searches'].append(strategy)
        
        results = []
        
        try:
            if strategy == "grep_search":
                results = self._grep_search(current_query, state['discovered_files'])
                
            elif strategy == "fuzzy_search":
                results = self._fuzzy_search(current_query, state['discovered_files'])
                
            elif strategy == "code_structure_analysis":
                results = self._code_structure_search(current_query, state['discovered_files'])
                
            elif strategy == "config_file_search":
                results = self._config_file_search(current_query, state['discovered_files'])
                
            elif strategy == "data_flow_analysis":
                results = self._data_flow_search(current_query, state['discovered_files'])
                
            elif strategy == "dense_retrieval":
                results = self._dense_retrieval_search(current_query, state['discovered_files'])
                
            elif strategy == "bm25_retrieval":
                results = self._bm25_retrieval_search(current_query, state['discovered_files'])
                
            elif strategy == "hybrid_retrieval":
                results = self._hybrid_retrieval_search(current_query, state['discovered_files'])
                
        except Exception as e:
            print(f"❌ Error in {strategy}: {e}")
            results = []
        
        # Add results to state
        state['all_results'].extend(results)
        
        print(f"✅ {strategy} found {len(results)} results")
        
        # Continue searching if more strategies remain
        if state['pending_searches']:
            return state
        else:
            state['status'] = ResearchStatus.ANALYZING
            return state
    
    def _grep_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Perform grep search."""
        # Extract key terms for grep
        terms = [term for term in query.split() if len(term) > 2]
        results = []
        
        for term in terms[:3]:  # Limit to first 3 terms
            grep_results = self.file_search_tool.grep_search(
                term, case_sensitive=False, context_lines=2
            )
            results.extend(grep_results)
        
        return results
    
    def _fuzzy_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Perform fuzzy search."""
        return self.file_search_tool.fuzzy_search(query, files, threshold=0.4)
    
    def _code_structure_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Search for code structures."""
        results = []
        code_files = [f for f in files if f.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c'))]
        
        for file_path in code_files[:20]:  # Limit for performance
            content = self.file_read_tool.read_file(file_path)
            if content:
                # Analyze code structure
                language = self._detect_language(file_path)
                structure = self.pattern_matcher.analyze_code_structure(content, language)
                
                # Check if query matches any structural elements
                query_lower = query.lower()
                relevance = 0.0
                matched_elements = []
                
                for element_type, elements in structure.items():
                    if isinstance(elements, list):
                        for element in elements:
                            if isinstance(element, str) and query_lower in element.lower():
                                relevance += 0.2
                                matched_elements.append(f"{element_type}: {element}")
                
                if relevance > 0:
                    results.append(SearchResult(
                        source=file_path,
                        content=f"Code structure matches: {', '.join(matched_elements[:5])}",
                        relevance_score=min(relevance, 1.0),
                        metadata={
                            "matched_elements": matched_elements,
                            "structure": structure
                        },
                        search_query=query,
                        tool_used="code_structure_analysis"
                    ))
        
        return results
    
    def _config_file_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Search configuration files."""
        config_files = [f for f in files if any(f.endswith(ext) for ext in 
                       ['.json', '.yaml', '.yml', '.ini', '.conf', '.config', '.env'])]
        
        results = []
        for file_path in config_files:
            content = self.file_read_tool.read_file(file_path)
            if content and query.lower() in content.lower():
                # Find specific lines containing the query
                lines = content.split('\n')
                matching_lines = []
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        matching_lines.append(f"Line {i+1}: {line.strip()}")
                
                if matching_lines:
                    results.append(SearchResult(
                        source=file_path,
                        content='\n'.join(matching_lines[:5]),
                        relevance_score=0.8,
                        metadata={"matching_lines": len(matching_lines)},
                        search_query=query,
                        tool_used="config_file_search"
                    ))
        
        return results
    
    def _data_flow_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Search for data flow patterns."""
        results = []
        
        # Look for data-related patterns
        data_patterns = [
            r'def\s+\w*(?:process|transform|parse|convert|load|save)\w*',
            r'class\s+\w*(?:Parser|Processor|Transformer|Loader|Handler)\w*',
            r'\w*(?:data|df|dataset|records|rows|columns)\w*\s*=',
        ]
        
        for file_path in files[:30]:  # Limit for performance
            content = self.file_read_tool.read_file(file_path)
            if content:
                for pattern in data_patterns:
                    matches = self.pattern_matcher.find_custom_pattern(content, pattern)
                    for match in matches:
                        if any(term.lower() in match['line_content'].lower() 
                              for term in query.split()):
                            results.append(SearchResult(
                                source=file_path,
                                content=match['line_content'],
                                relevance_score=0.7,
                                metadata={
                                    "line_number": match['line_number'],
                                    "pattern_type": "data_flow",
                                    "match": match['match']
                                },
                                search_query=query,
                                tool_used="data_flow_analysis"
                            ))
        
        return results
    
    def _dense_retrieval_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Perform dense retrieval search."""
        if self.dense_tool is None:
            self.dense_tool = DenseRetrievalTool(self.workspace_path)
            print("🔧 Building dense retrieval index...")
            self.dense_tool.index_documents(files[:50])  # Limit for performance
        
        return self.dense_tool.search(query, top_k=10)
    
    def _bm25_retrieval_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Perform BM25 retrieval search."""
        if self.bm25_tool is None:
            self.bm25_tool = BM25RetrievalTool(self.workspace_path)
            print("🔧 Building BM25 index...")
            self.bm25_tool.index_documents(files[:50])  # Limit for performance
        
        return self.bm25_tool.search(query, top_k=10)
    
    def _hybrid_retrieval_search(self, query: str, files: List[str]) -> List[SearchResult]:
        """Perform hybrid retrieval search."""
        if self.hybrid_tool is None:
            self.hybrid_tool = HybridRetrievalTool(self.workspace_path)
            print("🔧 Building hybrid retrieval index...")
            self.hybrid_tool.index_documents(files[:50])  # Limit for performance
        
        return self.hybrid_tool.search(query, top_k=10)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c'
        }
        return language_map.get(ext, 'generic')


class AnalysisNode:
    """Node for analyzing search results."""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.content_analyzer = ContentAnalyzer(workspace_path)
        
    def __call__(self, state: ResearchState) -> ResearchState:
        """Analyze search results and extract insights."""
        print(f"📊 Analyzing {len(state['all_results'])} search results")
        
        if not state['all_results']:
            state['status'] = ResearchStatus.COMPLETED
            state['research_report'] = "No relevant results found for the query."
            return state
        
        # Filter results by relevance threshold
        relevant_results = [r for r in state['all_results'] 
                          if r.relevance_score >= state['similarity_threshold']]
        
        if not relevant_results:
            relevant_results = sorted(state['all_results'], 
                                    key=lambda x: x.relevance_score, reverse=True)[:10]
        
        # Analyze content patterns
        analysis = self.content_analyzer.analyze_content_patterns(relevant_results)
        
        # Extract key insights
        insights = self.content_analyzer.extract_key_insights(relevant_results)
        
        # Generate follow-up questions
        follow_up_questions = self.content_analyzer.suggest_follow_up_queries(
            relevant_results, state['original_query']
        )
        
        # Create research iteration
        iteration = ResearchIteration(
            iteration_number=state['current_iteration'],
            query=state['current_query'] or state['original_query'],
            results=relevant_results,
            insights=insights,
            follow_up_questions=follow_up_questions,
            status=ResearchStatus.ANALYZING
        )
        
        state['iterations'].append(iteration)
        state['key_insights'].extend(insights)
        
        print(f"💡 Generated {len(insights)} insights")
        print(f"❓ Generated {len(follow_up_questions)} follow-up questions")
        
        # Decide next action
        if (state['current_iteration'] < state['max_iterations'] and 
            follow_up_questions and 
            len(relevant_results) < 20):  # Need more comprehensive results
            state['status'] = ResearchStatus.ITERATING
        else:
            state['status'] = ResearchStatus.SYNTHESIZING
            
        return state


class IterationNode:
    """Node for iterating research with follow-up queries."""
    
    def __init__(self):
        pass
        
    def __call__(self, state: ResearchState) -> ResearchState:
        """Plan next iteration of research."""
        print("🔄 Planning next research iteration")
        
        if not state['iterations']:
            state['status'] = ResearchStatus.SYNTHESIZING
            return state
        
        last_iteration = state['iterations'][-1]
        
        # Select best follow-up question
        if last_iteration.follow_up_questions:
            next_query = last_iteration.follow_up_questions[0]
            state['current_query'] = next_query
            state['current_iteration'] += 1
            
            # Reset search strategies for new query
            state['pending_searches'] = ["grep_search", "fuzzy_search"]
            
            # Add advanced strategies if needed
            if state['current_iteration'] > 1:
                state['pending_searches'].extend(["dense_retrieval", "bm25_retrieval"])
            
            state['completed_searches'] = []
            state['status'] = ResearchStatus.SEARCHING
            
            print(f"🎯 Next query: {next_query}")
        else:
            state['status'] = ResearchStatus.SYNTHESIZING
            
        return state


class SynthesisNode:
    """Node for synthesizing research findings."""
    
    def __init__(self):
        pass
        
    def __call__(self, state: ResearchState) -> ResearchState:
        """Synthesize all research findings."""
        print("🧠 Synthesizing research findings")
        
        # Calculate confidence score based on results quality
        confidence_factors = []
        
        if state['all_results']:
            avg_relevance = sum(r.relevance_score for r in state['all_results']) / len(state['all_results'])
            confidence_factors.append(min(avg_relevance * 2, 1.0))
            
            # Factor in number of iterations
            iteration_factor = min(len(state['iterations']) / 3, 1.0)
            confidence_factors.append(iteration_factor)
            
            # Factor in diversity of sources
            unique_sources = len(set(r.source for r in state['all_results']))
            source_factor = min(unique_sources / 10, 1.0)
            confidence_factors.append(source_factor)
        else:
            confidence_factors = [0.1]
        
        state['confidence_score'] = sum(confidence_factors) / len(confidence_factors)
        state['status'] = ResearchStatus.COMPLETED
        
        print(f"📈 Research confidence: {state['confidence_score']:.2f}")
        
        return state


class ReportNode:
    """Node for generating the final research report."""
    
    def __init__(self):
        pass
        
    def __call__(self, state: ResearchState) -> ResearchState:
        """Generate comprehensive research report."""
        print("📝 Generating research report")
        
        report_sections = []
        
        # Executive Summary
        report_sections.append("# Deep Research Report")
        report_sections.append(f"**Query:** {state['original_query']}")
        report_sections.append(f"**Confidence Score:** {state['confidence_score']:.2f}/1.0")
        report_sections.append(f"**Total Results:** {len(state['all_results'])}")
        report_sections.append(f"**Files Analyzed:** {len(set(r.source for r in state['all_results']))}")
        report_sections.append("")
        
        # Key Insights
        if state['key_insights']:
            report_sections.append("## Key Insights")
            for i, insight in enumerate(state['key_insights'][:10], 1):
                report_sections.append(f"{i}. {insight}")
            report_sections.append("")
        
        # Research Iterations
        if state['iterations']:
            report_sections.append("## Research Process")
            for iteration in state['iterations']:
                report_sections.append(f"### Iteration {iteration.iteration_number + 1}")
                report_sections.append(f"**Query:** {iteration.query}")
                report_sections.append(f"**Results Found:** {len(iteration.results)}")
                
                if iteration.insights:
                    report_sections.append("**Insights:**")
                    for insight in iteration.insights[:3]:
                        report_sections.append(f"- {insight}")
                
                report_sections.append("")
        
        # Top Results
        high_relevance_results = [r for r in state['all_results'] if r.relevance_score >= 0.7]
        if high_relevance_results:
            report_sections.append("## Most Relevant Findings")
            for i, result in enumerate(high_relevance_results[:5], 1):
                report_sections.append(f"### {i}. {result.source}")
                report_sections.append(f"**Relevance:** {result.relevance_score:.2f}")
                report_sections.append(f"**Tool Used:** {result.tool_used}")
                report_sections.append("**Content:**")
                report_sections.append(f"```\n{result.content[:300]}...\n```")
                report_sections.append("")
        
        # File Analysis
        file_stats = {}
        for result in state['all_results']:
            if result.source not in file_stats:
                file_stats[result.source] = {'count': 0, 'max_relevance': 0}
            file_stats[result.source]['count'] += 1
            file_stats[result.source]['max_relevance'] = max(
                file_stats[result.source]['max_relevance'], result.relevance_score
            )
        
        top_files = sorted(file_stats.items(), 
                          key=lambda x: (x[1]['count'], x[1]['max_relevance']), 
                          reverse=True)[:10]
        
        if top_files:
            report_sections.append("## File Analysis")
            report_sections.append("| File | Matches | Max Relevance |")
            report_sections.append("|------|---------|---------------|")
            for file_path, stats in top_files:
                report_sections.append(f"| {file_path} | {stats['count']} | {stats['max_relevance']:.2f} |")
            report_sections.append("")
        
        # Search Strategy Analysis
        tool_stats = {}
        for result in state['all_results']:
            tool = result.tool_used
            if tool not in tool_stats:
                tool_stats[tool] = {'count': 0, 'avg_relevance': 0}
            tool_stats[tool]['count'] += 1
            tool_stats[tool]['avg_relevance'] += result.relevance_score
        
        for tool in tool_stats:
            tool_stats[tool]['avg_relevance'] /= tool_stats[tool]['count']
        
        if tool_stats:
            report_sections.append("## Search Strategy Performance")
            report_sections.append("| Tool | Results | Avg Relevance |")
            report_sections.append("|------|---------|---------------|")
            for tool, stats in sorted(tool_stats.items(), key=lambda x: x[1]['avg_relevance'], reverse=True):
                report_sections.append(f"| {tool} | {stats['count']} | {stats['avg_relevance']:.2f} |")
            report_sections.append("")
        
        # Recommendations
        report_sections.append("## Recommendations")
        if state['confidence_score'] < 0.5:
            report_sections.append("- Consider refining the query for more specific results")
            report_sections.append("- Try alternative search terms or approaches")
        if len(state['all_results']) > 100:
            report_sections.append("- Results are comprehensive but may benefit from filtering")
        if len(set(r.source for r in state['all_results'])) < 5:
            report_sections.append("- Consider expanding search to include more file types")
        
        state['research_report'] = '\n'.join(report_sections)
        
        print("✅ Research report generated")
        
        return state