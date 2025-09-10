"""
Main entry point for the Deep Research LangGraph workflow.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .workflows.research_workflow import DeepResearchWorkflow
from .utils.helpers import (
    setup_logging, validate_workspace, format_results, 
    save_results, load_config
)


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Deep Research LangGraph Workflow - Intelligent file research system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic research
  python -m deep_research.main "find authentication code" --workspace /path/to/project
  
  # Advanced research with custom settings
  python -m deep_research.main "data processing pipeline" \\
    --workspace /path/to/project \\
    --max-iterations 5 \\
    --threshold 0.5 \\
    --output results.json \\
    --format json
  
  # Interactive mode
  python -m deep_research.main --interactive --workspace /path/to/project
        """
    )
    
    # Required arguments
    parser.add_argument(
        "query",
        nargs="?",
        help="Research query to investigate"
    )
    
    parser.add_argument(
        "--workspace", "-w",
        required=True,
        help="Path to the workspace/codebase to research"
    )
    
    # Optional arguments
    parser.add_argument(
        "--max-iterations", "-i",
        type=int,
        default=3,
        help="Maximum number of research iterations (default: 3)"
    )
    
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.3,
        help="Similarity threshold for results (default: 0.3)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path for results"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "text"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file path"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate workspace and exit"
    )
    
    parser.add_argument(
        "--show-graph",
        action="store_true",
        help="Show workflow graph and exit"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Load configuration if provided
    config = {}
    if args.config:
        config = load_config(args.config)
        print(f"📄 Loaded configuration from {args.config}")
    
    # Override config with command line arguments
    if args.max_iterations:
        config["max_iterations"] = args.max_iterations
    if args.threshold:
        config["similarity_threshold"] = args.threshold
    
    # Validate workspace
    print(f"🔍 Validating workspace: {args.workspace}")
    validation = validate_workspace(args.workspace)
    
    if not validation["valid"]:
        print("❌ Workspace validation failed:")
        for error in validation["errors"]:
            print(f"  - {error}")
        sys.exit(1)
    
    print(f"✅ Workspace validated:")
    print(f"  - Files: {validation['file_count']}")
    print(f"  - Directories: {validation['directory_count']}")
    print(f"  - Total size: {validation['total_size']:,} bytes")
    print(f"  - File types: {len(validation['file_types'])}")
    
    if args.validate_only:
        print("\n📊 File type distribution:")
        for ext, count in sorted(validation['file_types'].items(), 
                                key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ext}: {count}")
        return
    
    # Initialize workflow
    workflow = DeepResearchWorkflow(
        workspace_path=args.workspace,
        max_iterations=config.get("max_iterations", args.max_iterations),
        similarity_threshold=config.get("similarity_threshold", args.threshold)
    )
    
    if args.show_graph:
        print("🔄 Workflow Graph:")
        print(workflow.get_workflow_graph())
        return
    
    # Handle interactive mode
    if args.interactive:
        run_interactive_mode(workflow)
        return
    
    # Validate query
    if not args.query:
        print("❌ Query is required (use --interactive for interactive mode)")
        parser.print_help()
        sys.exit(1)
    
    # Run research
    try:
        results = workflow.run_research(args.query)
        
        # Format and display results
        if args.format == "json":
            formatted_results = json.dumps(results, indent=2, default=str)
        else:
            formatted_results = format_results(results, args.format)
        
        # Output results
        if args.output:
            success = save_results(results, args.output, args.format)
            if success:
                print(f"💾 Results saved to {args.output}")
            else:
                print(f"❌ Failed to save results to {args.output}")
        else:
            print("\n" + "="*60)
            print("RESEARCH RESULTS")
            print("="*60)
            print(formatted_results)
        
        # Print summary
        print(f"\n📊 Research Summary:")
        print(f"  - Status: {results.get('status', 'Unknown')}")
        print(f"  - Confidence: {results.get('confidence_score', 0):.2f}")
        print(f"  - Results: {results.get('total_results', 0)}")
        print(f"  - Files: {results.get('files_analyzed', 0)}")
        print(f"  - Iterations: {results.get('iterations', 0)}")
        
    except KeyboardInterrupt:
        print("\n🛑 Research interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Research failed: {e}")
        sys.exit(1)


def run_interactive_mode(workflow: DeepResearchWorkflow):
    """Run the workflow in interactive mode."""
    print("\n🎯 Welcome to Deep Research Interactive Mode!")
    print("Type 'help' for commands, 'quit' to exit")
    
    while True:
        try:
            # Get user input
            query = input("\n🔍 Enter research query: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            
            elif query.lower() == "help":
                print_help()
                continue
            
            elif query.lower() == "graph":
                print("🔄 Workflow Graph:")
                print(workflow.get_workflow_graph())
                continue
            
            elif query.lower() == "stats":
                validation = validate_workspace(workflow.workspace_path)
                print(f"\n📊 Workspace Statistics:")
                print(f"  - Files: {validation['file_count']}")
                print(f"  - Directories: {validation['directory_count']}")
                print(f"  - Total size: {validation['total_size']:,} bytes")
                continue
            
            # Run research
            print(f"\n🚀 Researching: {query}")
            results = workflow.run_research(query)
            
            # Display results
            print(f"\n📊 Research Complete!")
            print(f"  - Status: {results.get('status', 'Unknown')}")
            print(f"  - Confidence: {results.get('confidence_score', 0):.2f}")
            print(f"  - Results: {results.get('total_results', 0)}")
            print(f"  - Files: {results.get('files_analyzed', 0)}")
            
            # Show key insights
            insights = results.get('key_insights', [])
            if insights:
                print(f"\n💡 Key Insights:")
                for i, insight in enumerate(insights[:5], 1):
                    print(f"  {i}. {insight}")
            
            # Show top results
            top_results = results.get('top_results', [])
            if top_results:
                print(f"\n🎯 Top Results:")
                for i, result in enumerate(top_results[:3], 1):
                    print(f"  {i}. {result.get('source', 'Unknown')} "
                          f"(Score: {result.get('relevance_score', 0):.2f})")
            
            # Ask if user wants to save results
            save_choice = input("\n💾 Save results to file? (y/n): ").strip().lower()
            if save_choice in ["y", "yes"]:
                filename = input("📁 Enter filename (default: results.json): ").strip()
                if not filename:
                    filename = "results.json"
                
                if save_results(results, filename, "json"):
                    print(f"✅ Results saved to {filename}")
                else:
                    print(f"❌ Failed to save results")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def print_help():
    """Print help information for interactive mode."""
    print("""
🎯 Deep Research Interactive Mode Commands:

Research Commands:
  <query>           - Run research on the given query
  
Utility Commands:
  help             - Show this help message
  graph            - Show workflow graph
  stats            - Show workspace statistics
  quit/exit/q      - Exit interactive mode

Examples:
  find authentication methods
  analyze data processing pipeline  
  search for configuration files
  locate error handling code
    """)


if __name__ == "__main__":
    main()