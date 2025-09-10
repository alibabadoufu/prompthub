"""
Demo script for the Deep Research LangGraph workflow.
"""

import os
import json
from pathlib import Path

from deep_research.workflows.research_workflow import DeepResearchWorkflow
from deep_research.utils.helpers import setup_logging, validate_workspace


def run_demo():
    """Run a comprehensive demo of the deep research system."""
    print("🚀 Deep Research LangGraph Workflow Demo")
    print("=" * 60)
    
    # Setup logging
    setup_logging("INFO")
    
    # Use current workspace as demo
    workspace_path = "/workspace"
    
    print(f"📁 Demo workspace: {workspace_path}")
    
    # Validate workspace
    validation = validate_workspace(workspace_path)
    print(f"✅ Workspace validation: {'✓' if validation['valid'] else '✗'}")
    print(f"📊 Files: {validation['file_count']}, Directories: {validation['directory_count']}")
    
    if not validation["valid"]:
        print("❌ Cannot proceed with invalid workspace")
        return
    
    # Initialize workflow
    workflow = DeepResearchWorkflow(
        workspace_path=workspace_path,
        max_iterations=2,  # Keep demo short
        similarity_threshold=0.3
    )
    
    # Demo queries
    demo_queries = [
        "gradio application configuration",
        "database and data management",
        "LLM client implementation",
        "file processing and utilities"
    ]
    
    results_summary = []
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Demo Query {i}: {query}")
        print(f"{'='*60}")
        
        try:
            # Run research
            results = workflow.run_research(query)
            
            # Display summary
            print(f"\n📊 Results Summary:")
            print(f"  - Status: {results.get('status', 'Unknown')}")
            print(f"  - Confidence: {results.get('confidence_score', 0):.2f}")
            print(f"  - Total Results: {results.get('total_results', 0)}")
            print(f"  - Files Analyzed: {results.get('files_analyzed', 0)}")
            print(f"  - Iterations: {results.get('iterations', 0)}")
            
            # Show key insights
            insights = results.get('key_insights', [])
            if insights:
                print(f"\n💡 Key Insights:")
                for insight in insights[:3]:
                    print(f"  • {insight}")
            
            # Show top results
            top_results = results.get('top_results', [])
            if top_results:
                print(f"\n🎯 Top Results:")
                for j, result in enumerate(top_results[:3], 1):
                    print(f"  {j}. {result.get('source', 'Unknown')} "
                          f"(Relevance: {result.get('relevance_score', 0):.2f})")
                    print(f"     Tool: {result.get('tool_used', 'Unknown')}")
                    content_preview = result.get('content', '')[:100]
                    print(f"     Preview: {content_preview}...")
            
            # Save detailed results
            output_file = f"demo_results_{i}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to {output_file}")
            
            # Add to summary
            results_summary.append({
                "query": query,
                "confidence": results.get('confidence_score', 0),
                "total_results": results.get('total_results', 0),
                "files_analyzed": results.get('files_analyzed', 0),
                "top_insights": insights[:3] if insights else []
            })
            
        except Exception as e:
            print(f"❌ Error processing query '{query}': {e}")
            results_summary.append({
                "query": query,
                "error": str(e)
            })
    
    # Overall summary
    print(f"\n{'='*60}")
    print("📋 DEMO SUMMARY")
    print(f"{'='*60}")
    
    for i, summary in enumerate(results_summary, 1):
        print(f"\nQuery {i}: {summary['query']}")
        if 'error' in summary:
            print(f"  ❌ Error: {summary['error']}")
        else:
            print(f"  ✅ Confidence: {summary['confidence']:.2f}")
            print(f"  📊 Results: {summary['total_results']}")
            print(f"  📁 Files: {summary['files_analyzed']}")
            if summary['top_insights']:
                print(f"  💡 Key Insight: {summary['top_insights'][0]}")
    
    print(f"\n🎉 Demo completed! Check the generated demo_results_*.json files for detailed analysis.")


def interactive_demo():
    """Run interactive demo."""
    print("🎯 Interactive Deep Research Demo")
    print("Type your research queries (or 'quit' to exit)")
    
    workspace_path = "/workspace"
    workflow = DeepResearchWorkflow(workspace_path, max_iterations=2)
    
    while True:
        try:
            query = input("\n🔍 Research query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Demo finished!")
                break
            
            if not query:
                continue
            
            print(f"\n🚀 Researching: {query}")
            results = workflow.run_research(query)
            
            # Quick summary
            print(f"\n📊 Quick Summary:")
            print(f"  Confidence: {results.get('confidence_score', 0):.2f}")
            print(f"  Results: {results.get('total_results', 0)}")
            print(f"  Files: {results.get('files_analyzed', 0)}")
            
            # Top insight
            insights = results.get('key_insights', [])
            if insights:
                print(f"  Key Insight: {insights[0]}")
            
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        run_demo()