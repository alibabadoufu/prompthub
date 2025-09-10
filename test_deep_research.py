"""
Quick test script for the Deep Research LangGraph workflow.
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        from deep_research.models.state import ResearchState, SearchResult
        from deep_research.tools.file_tools import FileSearchTool, FileListTool
        from deep_research.tools.retrieval_tools import DenseRetrievalTool, BM25RetrievalTool
        from deep_research.tools.analysis_tools import ContentAnalyzer, PatternMatcher
        from deep_research.nodes.research_nodes import PlanningNode, SearchNode
        from deep_research.workflows.research_workflow import DeepResearchWorkflow
        from deep_research.utils.helpers import validate_workspace
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_file_tools():
    """Test file tools functionality."""
    print("\n🔍 Testing file tools...")
    
    try:
        from deep_research.tools.file_tools import FileListTool, FileSearchTool
        
        # Test file listing
        file_list_tool = FileListTool("/workspace")
        files = file_list_tool.list_files("*.py")
        print(f"✅ Found {len(files)} Python files")
        
        # Test file search
        file_search_tool = FileSearchTool("/workspace")
        results = file_search_tool.grep_search("import", file_types=["py"])
        print(f"✅ Grep search found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ File tools error: {e}")
        traceback.print_exc()
        return False


def test_workflow_creation():
    """Test workflow creation."""
    print("\n🔍 Testing workflow creation...")
    
    try:
        from deep_research.workflows.research_workflow import DeepResearchWorkflow
        
        workflow = DeepResearchWorkflow("/workspace", max_iterations=1)
        print("✅ Workflow created successfully")
        
        # Test state creation
        state = workflow.create_initial_state("test query")
        print("✅ Initial state created")
        print(f"   Query: {state['original_query']}")
        print(f"   Status: {state['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow creation error: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Test basic functionality without running full workflow."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        from deep_research.utils.helpers import validate_workspace
        from deep_research.tools.file_tools import FileListTool
        
        # Test workspace validation
        validation = validate_workspace("/workspace")
        print(f"✅ Workspace validation: {validation['valid']}")
        print(f"   Files: {validation['file_count']}")
        print(f"   Directories: {validation['directory_count']}")
        
        # Test content analysis
        from deep_research.tools.analysis_tools import ContentAnalyzer
        analyzer = ContentAnalyzer("/workspace")
        
        # Create some mock results for testing
        from deep_research.models.state import SearchResult
        mock_results = [
            SearchResult(
                source="test.py",
                content="def test_function(): pass",
                relevance_score=0.8,
                metadata={},
                search_query="test",
                tool_used="mock"
            )
        ]
        
        insights = analyzer.extract_key_insights(mock_results)
        print(f"✅ Content analysis generated {len(insights)} insights")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🧪 Deep Research System Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("File Tools", test_file_tools),
        ("Workflow Creation", test_workflow_creation),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTry running:")
        print("  python deep_research_demo.py")
        print("  python -m deep_research.main 'test query' --workspace /workspace")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())