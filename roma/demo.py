#!/usr/bin/env python3
"""
ROMA Research Agent - Demonstration Script

This script demonstrates the capabilities of the ROMA research agent
by running a sample analysis on the provided test data.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the roma package to the path
sys.path.insert(0, str(Path(__file__).parent))

from workflows.deep_research_workflow import DeepResearchWorkflow
from utils.logging_utils import setup_logging
from config.settings import get_settings


async def run_demo():
    """Run a demonstration of the ROMA research agent."""
    
    # Setup logging
    setup_logging(level="INFO")
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ROMA Research Agent Demonstration")
    
    # Get settings
    settings = get_settings()
    
    # Create workflow
    workflow_config = {
        'max_concurrent_files': settings.workflow.max_concurrent_files,
        'max_concurrent_analysis': settings.workflow.max_concurrent_analysis
    }
    
    workflow = DeepResearchWorkflow(workflow_config)
    
    # Demo 1: Analyze sample data directory
    sample_data_dir = Path(__file__).parent / "data" / "sample_files"
    
    if sample_data_dir.exists():
        logger.info("=== Demo 1: Analyzing Sample Data ===")
        
        results = await workflow.run_research(
            directory_path=str(sample_data_dir),
            query="Python code analysis and configuration",
            query_keywords=["python", "configuration", "api", "processing"],
            research_depth="medium",
            max_results=20
        )
        
        if results["success"]:
            logger.info(f"Demo 1 completed successfully!")
            logger.info(f"Found {len(results['findings'])} research findings")
            
            # Print a brief summary
            print("\n" + "="*60)
            print("ROMA RESEARCH AGENT - DEMO RESULTS")
            print("="*60)
            print(f"Query: {results['query']}")
            print(f"Directory: {results['directory_path']}")
            print(f"Processing Time: {results['processing_time']}")
            print(f"Findings: {len(results['findings'])}")
            
            # Show statistics
            stats = results.get('statistics', {})
            file_stats = stats.get('file_stats', {})
            analysis_stats = stats.get('analysis_stats', {})
            
            print(f"\nFile Statistics:")
            print(f"  - Total files: {file_stats.get('total_files', 0)}")
            print(f"  - Supported files: {file_stats.get('supported_files', 0)}")
            print(f"  - Total size: {file_stats.get('total_size', 0) / 1024:.1f} KB")
            
            print(f"\nAnalysis Statistics:")
            print(f"  - Files analyzed: {analysis_stats.get('total_files_analyzed', 0)}")
            print(f"  - Keywords found: {analysis_stats.get('total_keywords', 0)}")
            print(f"  - Average complexity: {analysis_stats.get('avg_complexity_score', 0):.2f}")
            
            # Show top findings
            print(f"\nTop Research Findings:")
            for i, finding in enumerate(results['findings'][:3], 1):
                print(f"  {i}. {finding['source_file']} (confidence: {finding['confidence']:.2f})")
                print(f"     Keywords: {', '.join(finding['keywords'][:5])}")
                print(f"     Content preview: {finding['content'][:100]}...")
                print()
            
            print("="*60)
            
        else:
            logger.error(f"Demo 1 failed: {results.get('error', 'Unknown error')}")
    
    else:
        logger.warning("Sample data directory not found, skipping demo")
    
    # Demo 2: Analyze the ROMA codebase itself
    logger.info("=== Demo 2: Self-Analysis of ROMA Codebase ===")
    
    roma_dir = Path(__file__).parent
    
    results = await workflow.run_research(
        directory_path=str(roma_dir),
        query="LangGraph workflow implementation and node architecture",
        query_keywords=["langgraph", "workflow", "node", "async", "processing"],
        file_patterns=["*.py"],
        research_depth="deep",
        max_results=15
    )
    
    if results["success"]:
        logger.info(f"Demo 2 completed successfully!")
        logger.info(f"Found {len(results['findings'])} research findings")
        
        print(f"\nSelf-Analysis Results:")
        print(f"  - Analyzed {results['statistics']['file_stats']['total_files']} Python files")
        print(f"  - Found {len(results['findings'])} relevant findings")
        print(f"  - Processing time: {results['processing_time']}")
        
        # Show workflow info
        workflow_info = workflow.get_workflow_info()
        print(f"\nWorkflow Information:")
        print(f"  - Name: {workflow_info['name']}")
        print(f"  - Version: {workflow_info['version']}")
        print(f"  - Nodes: {len(workflow_info['nodes'])}")
        
        for node in workflow_info['nodes']:
            print(f"    * {node['name']}: {node['type']}")
    
    else:
        logger.error(f"Demo 2 failed: {results.get('error', 'Unknown error')}")
    
    logger.info("ROMA Research Agent Demonstration completed")


def main():
    """Main function for the demo."""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()