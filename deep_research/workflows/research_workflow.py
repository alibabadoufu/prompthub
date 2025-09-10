"""
Main LangGraph workflow for deep research on local files.
"""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models.state import ResearchState, ResearchStatus
from ..nodes.research_nodes import (
    PlanningNode, SearchNode, AnalysisNode, 
    IterationNode, SynthesisNode, ReportNode
)


class DeepResearchWorkflow:
    """Main workflow orchestrator for deep research."""
    
    def __init__(self, workspace_path: str, max_iterations: int = 3, 
                 similarity_threshold: float = 0.3):
        self.workspace_path = workspace_path
        self.max_iterations = max_iterations
        self.similarity_threshold = similarity_threshold
        
        # Initialize nodes
        self.planning_node = PlanningNode(workspace_path)
        self.search_node = SearchNode(workspace_path)
        self.analysis_node = AnalysisNode(workspace_path)
        self.iteration_node = IterationNode()
        self.synthesis_node = SynthesisNode()
        self.report_node = ReportNode()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create the state graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("planning", self.planning_node)
        workflow.add_node("search", self.search_node)
        workflow.add_node("analysis", self.analysis_node)
        workflow.add_node("iteration", self.iteration_node)
        workflow.add_node("synthesis", self.synthesis_node)
        workflow.add_node("report", self.report_node)
        
        # Define the flow
        workflow.set_entry_point("planning")
        
        # Planning -> Search
        workflow.add_edge("planning", "search")
        
        # Search -> Analysis (when search is complete)
        workflow.add_conditional_edges(
            "search",
            self._search_condition,
            {
                "continue_search": "search",
                "analyze": "analysis"
            }
        )
        
        # Analysis -> Iteration or Synthesis
        workflow.add_conditional_edges(
            "analysis",
            self._analysis_condition,
            {
                "iterate": "iteration",
                "synthesize": "synthesis"
            }
        )
        
        # Iteration -> Search (for next iteration)
        workflow.add_edge("iteration", "search")
        
        # Synthesis -> Report
        workflow.add_edge("synthesis", "report")
        
        # Report -> END
        workflow.add_edge("report", END)
        
        return workflow
    
    def _search_condition(self, state: ResearchState) -> str:
        """Determine if search should continue or move to analysis."""
        if state['pending_searches']:
            return "continue_search"
        else:
            return "analyze"
    
    def _analysis_condition(self, state: ResearchState) -> str:
        """Determine if we should iterate or synthesize."""
        if state['status'] == ResearchStatus.ITERATING:
            return "iterate"
        else:
            return "synthesize"
    
    def create_initial_state(self, query: str, research_goal: Optional[str] = None) -> ResearchState:
        """Create initial state for the research workflow."""
        return ResearchState(
            original_query=query,
            current_query=query,
            research_goal=research_goal or f"Deep research on: {query}",
            iterations=[],
            current_iteration=0,
            status=ResearchStatus.PLANNING,
            all_results=[],
            key_insights=[],
            discovered_files=[],
            search_strategies=[],
            completed_searches=[],
            pending_searches=[],
            research_report=None,
            confidence_score=0.0,
            max_iterations=self.max_iterations,
            similarity_threshold=self.similarity_threshold,
            workspace_path=self.workspace_path
        )
    
    def run_research(self, query: str, research_goal: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete research workflow."""
        print("🚀 Starting Deep Research Workflow")
        print(f"📝 Query: {query}")
        
        # Create initial state
        initial_state = self.create_initial_state(query, research_goal)
        
        # Compile the workflow with memory
        memory = MemorySaver()
        app = self.workflow.compile(checkpointer=memory)
        
        # Run the workflow
        config = {"configurable": {"thread_id": "research_session"}}
        
        try:
            # Execute the workflow
            final_state = None
            step_count = 0
            
            for state in app.stream(initial_state, config=config):
                step_count += 1
                print(f"\n--- Step {step_count} ---")
                
                # Get the current node name and state
                for node_name, node_state in state.items():
                    print(f"🔄 Executed: {node_name}")
                    final_state = node_state
                    
                    # Print current status
                    status = node_state.get('status', 'unknown')
                    print(f"📊 Status: {status.value if hasattr(status, 'value') else status}")
                    
                    # Print progress info
                    if 'all_results' in node_state:
                        print(f"📈 Total results: {len(node_state['all_results'])}")
                    if 'current_iteration' in node_state:
                        print(f"🔄 Iteration: {node_state['current_iteration']}")
                
                # Safety check for infinite loops
                if step_count > 20:
                    print("⚠️  Maximum steps reached, stopping workflow")
                    break
            
            if final_state:
                return self._format_results(final_state)
            else:
                return {"error": "Workflow did not complete successfully"}
                
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            return {"error": str(e)}
    
    def _format_results(self, final_state: ResearchState) -> Dict[str, Any]:
        """Format the final results for output."""
        return {
            "query": final_state['original_query'],
            "status": final_state['status'].value if hasattr(final_state['status'], 'value') else str(final_state['status']),
            "confidence_score": final_state['confidence_score'],
            "total_results": len(final_state['all_results']),
            "iterations": len(final_state['iterations']),
            "files_analyzed": len(set(r.source for r in final_state['all_results'])) if final_state['all_results'] else 0,
            "key_insights": final_state['key_insights'],
            "research_report": final_state['research_report'],
            "top_results": [
                {
                    "source": r.source,
                    "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                    "relevance_score": r.relevance_score,
                    "tool_used": r.tool_used
                }
                for r in sorted(final_state['all_results'], 
                              key=lambda x: x.relevance_score, reverse=True)[:10]
            ] if final_state['all_results'] else [],
            "search_strategies_used": final_state['completed_searches'],
            "discovered_files_count": len(final_state['discovered_files'])
        }
    
    def get_workflow_graph(self) -> str:
        """Get a visual representation of the workflow graph."""
        try:
            return self.workflow.get_graph().draw_mermaid()
        except:
            return """
            graph TD
                A[Planning] --> B[Search]
                B --> B
                B --> C[Analysis]
                C --> D[Iteration]
                C --> E[Synthesis]
                D --> B
                E --> F[Report]
                F --> G[End]
            """