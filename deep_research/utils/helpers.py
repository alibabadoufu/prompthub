"""
Helper utilities for the deep research workflow.
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_workspace(workspace_path: str) -> Dict[str, Any]:
    """Validate workspace and return information about it."""
    workspace = Path(workspace_path)
    
    validation_result = {
        "valid": False,
        "exists": False,
        "readable": False,
        "file_count": 0,
        "directory_count": 0,
        "total_size": 0,
        "file_types": {},
        "errors": []
    }
    
    try:
        # Check if workspace exists
        if not workspace.exists():
            validation_result["errors"].append("Workspace path does not exist")
            return validation_result
        
        validation_result["exists"] = True
        
        # Check if readable
        if not os.access(workspace, os.R_OK):
            validation_result["errors"].append("Workspace is not readable")
            return validation_result
        
        validation_result["readable"] = True
        
        # Analyze workspace contents
        file_count = 0
        directory_count = 0
        total_size = 0
        file_types = {}
        
        for item in workspace.rglob("*"):
            if item.is_file():
                file_count += 1
                try:
                    size = item.stat().st_size
                    total_size += size
                    
                    # Track file types
                    suffix = item.suffix.lower()
                    if suffix:
                        file_types[suffix] = file_types.get(suffix, 0) + 1
                    else:
                        file_types["no_extension"] = file_types.get("no_extension", 0) + 1
                        
                except (OSError, PermissionError):
                    # Skip files we can't access
                    pass
                    
            elif item.is_dir():
                directory_count += 1
        
        validation_result.update({
            "valid": True,
            "file_count": file_count,
            "directory_count": directory_count,
            "total_size": total_size,
            "file_types": file_types
        })
        
    except Exception as e:
        validation_result["errors"].append(f"Validation error: {str(e)}")
    
    return validation_result


def format_results(results: Dict[str, Any], output_format: str = "json") -> str:
    """Format research results for output."""
    if output_format.lower() == "json":
        return json.dumps(results, indent=2, default=str)
    
    elif output_format.lower() == "markdown":
        return _format_markdown(results)
    
    elif output_format.lower() == "text":
        return _format_text(results)
    
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def _format_markdown(results: Dict[str, Any]) -> str:
    """Format results as markdown."""
    lines = []
    
    # Header
    lines.append("# Deep Research Results")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append(f"- **Query:** {results.get('query', 'N/A')}")
    lines.append(f"- **Status:** {results.get('status', 'N/A')}")
    lines.append(f"- **Confidence:** {results.get('confidence_score', 0):.2f}")
    lines.append(f"- **Total Results:** {results.get('total_results', 0)}")
    lines.append(f"- **Files Analyzed:** {results.get('files_analyzed', 0)}")
    lines.append(f"- **Iterations:** {results.get('iterations', 0)}")
    lines.append("")
    
    # Key Insights
    insights = results.get('key_insights', [])
    if insights:
        lines.append("## Key Insights")
        for i, insight in enumerate(insights, 1):
            lines.append(f"{i}. {insight}")
        lines.append("")
    
    # Top Results
    top_results = results.get('top_results', [])
    if top_results:
        lines.append("## Top Results")
        for i, result in enumerate(top_results, 1):
            lines.append(f"### {i}. {result.get('source', 'Unknown')}")
            lines.append(f"**Relevance:** {result.get('relevance_score', 0):.2f}")
            lines.append(f"**Tool:** {result.get('tool_used', 'Unknown')}")
            lines.append("**Content:**")
            lines.append(f"```\n{result.get('content', 'No content')}\n```")
            lines.append("")
    
    # Research Report
    report = results.get('research_report')
    if report:
        lines.append("## Detailed Report")
        lines.append(report)
    
    return "\n".join(lines)


def _format_text(results: Dict[str, Any]) -> str:
    """Format results as plain text."""
    lines = []
    
    # Header
    lines.append("=" * 60)
    lines.append("DEEP RESEARCH RESULTS")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Query: {results.get('query', 'N/A')}")
    lines.append(f"Status: {results.get('status', 'N/A')}")
    lines.append(f"Confidence: {results.get('confidence_score', 0):.2f}")
    lines.append(f"Total Results: {results.get('total_results', 0)}")
    lines.append(f"Files Analyzed: {results.get('files_analyzed', 0)}")
    lines.append(f"Iterations: {results.get('iterations', 0)}")
    lines.append("")
    
    # Key Insights
    insights = results.get('key_insights', [])
    if insights:
        lines.append("KEY INSIGHTS")
        lines.append("-" * 30)
        for i, insight in enumerate(insights, 1):
            lines.append(f"{i}. {insight}")
        lines.append("")
    
    # Top Results
    top_results = results.get('top_results', [])
    if top_results:
        lines.append("TOP RESULTS")
        lines.append("-" * 30)
        for i, result in enumerate(top_results, 1):
            lines.append(f"{i}. {result.get('source', 'Unknown')} "
                        f"(Relevance: {result.get('relevance_score', 0):.2f})")
            lines.append(f"   Tool: {result.get('tool_used', 'Unknown')}")
            lines.append(f"   Content: {result.get('content', 'No content')[:100]}...")
            lines.append("")
    
    return "\n".join(lines)


def save_results(results: Dict[str, Any], output_path: str, 
                format_type: str = "json") -> bool:
    """Save research results to file."""
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        formatted_content = format_results(results, format_type)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to save results: {e}")
        return False


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.json':
                return json.load(f)
            elif config_file.suffix.lower() in ['.yaml', '.yml']:
                import yaml
                return yaml.safe_load(f)
            else:
                return {}
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return {}


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get detailed information about a file."""
    file_obj = Path(file_path)
    
    info = {
        "exists": False,
        "size": 0,
        "modified": None,
        "extension": "",
        "is_text": False,
        "line_count": 0,
        "word_count": 0,
        "char_count": 0
    }
    
    if not file_obj.exists():
        return info
    
    try:
        stat = file_obj.stat()
        info.update({
            "exists": True,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_obj.suffix.lower()
        })
        
        # Check if it's a text file
        try:
            with open(file_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                info.update({
                    "is_text": True,
                    "line_count": len(content.split('\n')),
                    "word_count": len(content.split()),
                    "char_count": len(content)
                })
        except:
            info["is_text"] = False
            
    except Exception as e:
        logging.error(f"Error getting file info for {file_path}: {e}")
    
    return info