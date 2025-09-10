#!/usr/bin/env python3
"""
ROMA Research Agent - Main Entry Point

A Python-based LangGraph workflow for deep research on local files.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, List
import logging

from .config.settings import get_settings
from .utils.logging_utils import setup_logging
from .workflows.deep_research_workflow import DeepResearchWorkflow


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="ROMA Research Agent - Deep research on local files using LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic research on current directory
  python -m roma.main --directory . --query "machine learning algorithms"
  
  # Research with specific keywords and file types
  python -m roma.main --directory ./src --keywords "python" "flask" "api" --patterns "*.py"
  
  # Deep research with custom output
  python -m roma.main --directory ./docs --query "installation guide" --depth deep --output report.md
  
  # Research with configuration file
  python -m roma.main --directory . --query "database" --config ./my_config.yaml
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--directory", "-d",
        type=str,
        required=True,
        help="Directory path to analyze"
    )
    
    # Query arguments
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument(
        "--query", "-q",
        type=str,
        help="Research query string"
    )
    query_group.add_argument(
        "--keywords", "-k",
        nargs="+",
        help="List of keywords to search for"
    )
    
    # Optional arguments
    parser.add_argument(
        "--patterns", "-p",
        nargs="+",
        help="File patterns to include (e.g., '*.py', '*.md')"
    )
    
    parser.add_argument(
        "--depth",
        choices=["shallow", "medium", "deep"],
        default="medium",
        help="Research depth (default: medium)"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Maximum number of results (default: 50)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path for the report (default: stdout)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--thread-id",
        type=str,
        help="Thread ID for workflow checkpointing"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="ROMA Research Agent 1.0.0"
    )
    
    return parser


async def run_research_workflow(args: argparse.Namespace) -> dict:
    """Run the research workflow with given arguments."""
    
    # Load settings
    settings = get_settings(args.config)
    
    # Override settings with command line arguments
    if hasattr(args, 'log_level') and args.log_level:
        settings.logging.level = args.log_level
    if hasattr(args, 'log_file') and args.log_file:
        settings.logging.log_file = args.log_file
    
    # Setup logging
    setup_logging(
        level=settings.logging.level,
        log_file=settings.logging.log_file,
        format_string=settings.logging.format
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting ROMA Research Agent")
    
    # Validate directory
    directory_path = Path(args.directory)
    if not directory_path.exists():
        raise ValueError(f"Directory does not exist: {directory_path}")
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    # Prepare workflow configuration
    workflow_config = {
        'max_concurrent_files': settings.workflow.max_concurrent_files,
        'max_concurrent_analysis': settings.workflow.max_concurrent_analysis
    }
    
    # Create workflow
    workflow = DeepResearchWorkflow(workflow_config)
    
    # Prepare parameters
    query = args.query
    keywords = args.keywords
    
    # If keywords are provided but no query, create query from keywords
    if keywords and not query:
        query = " ".join(keywords)
    
    # Run research
    results = await workflow.run_research(
        directory_path=str(directory_path),
        query=query,
        query_keywords=keywords,
        file_patterns=args.patterns,
        research_depth=args.depth,
        max_results=args.max_results,
        thread_id=args.thread_id
    )
    
    return results


def format_results_text(results: dict) -> str:
    """Format results as human-readable text."""
    if not results.get("success", False):
        return f"Error: {results.get('error', 'Unknown error occurred')}"
    
    report = results.get("report", "No report generated")
    return report


def format_results_json(results: dict) -> str:
    """Format results as JSON."""
    # Create a simplified version for JSON output
    json_results = {
        "success": results.get("success", False),
        "query": results.get("query", ""),
        "directory_path": results.get("directory_path", ""),
        "processing_time": results.get("processing_time", ""),
        "statistics": results.get("statistics", {}),
        "findings_count": len(results.get("findings", [])),
        "findings": results.get("findings", []),
        "errors": results.get("errors", []),
        "warnings": results.get("warnings", [])
    }
    
    if not results.get("success", False):
        json_results["error"] = results.get("error", "Unknown error")
    
    return json.dumps(json_results, indent=2, ensure_ascii=False)


def save_output(content: str, output_path: str):
    """Save content to file."""
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error saving output to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


async def main():
    """Main entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        # Run the research workflow
        results = await run_research_workflow(args)
        
        # Format output
        if args.json_output:
            output_content = format_results_json(results)
        else:
            output_content = format_results_text(results)
        
        # Save or print output
        if args.output:
            save_output(output_content, args.output)
        else:
            print(output_content)
        
        # Exit with appropriate code
        if results.get("success", False):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cli_main():
    """CLI entry point for setuptools."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())