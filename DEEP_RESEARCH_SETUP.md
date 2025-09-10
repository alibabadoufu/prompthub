# Deep Research LangGraph Workflow - Setup Guide

## 🚀 Quick Start

### Option 1: Simple Demo (No Dependencies)
```bash
# Run basic file analysis demo
python3 deep_research_simple_demo.py

# Interactive simple demo
python3 deep_research_simple_demo.py --interactive
```

### Option 2: Full System (With Dependencies)
```bash
# Install dependencies
python3 install_deep_research.py

# Run comprehensive demo
python3 deep_research_demo.py

# Interactive full system
python3 -m deep_research.main --interactive --workspace /workspace

# Command-line usage
python3 -m deep_research.main "find authentication code" --workspace /workspace
```

## 📁 Project Structure

```
deep_research/
├── __init__.py                 # Package initialization
├── __main__.py                 # Module entry point
├── main.py                     # CLI application
├── models/
│   ├── __init__.py
│   └── state.py               # State management & data models
├── tools/
│   ├── __init__.py
│   ├── file_tools.py          # File search, list, read operations
│   ├── retrieval_tools.py     # Dense, BM25, hybrid retrieval
│   └── analysis_tools.py      # Content analysis & pattern matching
├── nodes/
│   ├── __init__.py
│   └── research_nodes.py      # LangGraph workflow nodes
├── workflows/
│   ├── __init__.py
│   └── research_workflow.py   # Main LangGraph workflow
└── utils/
    ├── __init__.py
    └── helpers.py             # Utility functions

# Demo & Setup Files
deep_research_demo.py           # Full system demo
deep_research_simple_demo.py    # Simple demo (no dependencies)
install_deep_research.py        # Dependency installer
test_deep_research.py          # Test suite
```

## 🧪 Testing the System

### 1. Simple Test (No Dependencies)
```bash
python3 deep_research_simple_demo.py
```
This runs basic file analysis and shows:
- File discovery and listing
- Text search across files
- Pattern analysis
- Relevance scoring

### 2. Full System Test (With Dependencies)
```bash
# Install dependencies first
python3 install_deep_research.py

# Run tests
python3 test_deep_research.py

# Run full demo
python3 deep_research_demo.py
```

## 🔧 Installation Options

### Manual Installation
```bash
pip install numpy>=1.24.0 langgraph>=0.0.40 langchain>=0.1.0 langchain-core>=0.1.0 pathlib2>=2.3.0
```

### Automatic Installation
```bash
python3 install_deep_research.py
```

### Using Requirements File
```bash
pip install -r requirements.txt
```

## 🎯 Usage Examples

### Command Line Interface
```bash
# Basic search
python3 -m deep_research.main "authentication methods" --workspace /path/to/code

# Advanced search with options
python3 -m deep_research.main "database connections" \
  --workspace /path/to/code \
  --max-iterations 5 \
  --threshold 0.4 \
  --output results.json \
  --format markdown

# Interactive mode
python3 -m deep_research.main --interactive --workspace /path/to/code

# Show workflow graph
python3 -m deep_research.main --show-graph --workspace /path/to/code

# Validate workspace only
python3 -m deep_research.main --validate-only --workspace /path/to/code
```

### Python API
```python
from deep_research.workflows.research_workflow import DeepResearchWorkflow

# Initialize
workflow = DeepResearchWorkflow(
    workspace_path="/path/to/code",
    max_iterations=3,
    similarity_threshold=0.3
)

# Run research
results = workflow.run_research("find error handling patterns")

# Access results
print(f"Confidence: {results['confidence_score']:.2f}")
print(f"Files analyzed: {results['files_analyzed']}")
for insight in results['key_insights']:
    print(f"- {insight}")
```

## 📊 Output Formats

### JSON Output
```json
{
  "query": "authentication methods",
  "status": "completed",
  "confidence_score": 0.85,
  "total_results": 42,
  "files_analyzed": 15,
  "key_insights": ["Found JWT implementation in auth.py", "..."],
  "top_results": [...]
}
```

### Markdown Report
```markdown
# Deep Research Report
**Query:** authentication methods
**Confidence Score:** 0.85/1.0

## Key Insights
1. Found JWT implementation in auth.py
2. Password hashing uses bcrypt

## Most Relevant Findings
### 1. auth.py (Relevance: 0.95)
```

### Text Report
```
DEEP RESEARCH RESULTS
====================
Query: authentication methods
Confidence: 0.85
Results: 42
Files: 15
```

## 🔍 Search Capabilities

### File-Based Tools
- **Grep Search**: Pattern matching with context
- **Fuzzy Search**: Approximate text matching  
- **Regex Search**: Complex pattern matching
- **File Listing**: Discovery and categorization

### Advanced Retrieval
- **Dense Retrieval**: TF-IDF semantic search
- **BM25 Retrieval**: Statistical ranking
- **Hybrid Retrieval**: Combined approach

### Code Analysis
- **Structure Analysis**: Functions, classes, imports
- **Pattern Matching**: Code patterns and relationships
- **Content Analysis**: Themes and insights
- **Relationship Discovery**: File connections

### Workflow Features
- **Iterative Research**: Multi-step investigation
- **Follow-up Queries**: Automatic query generation
- **Confidence Scoring**: Result quality assessment
- **Comprehensive Reporting**: Detailed analysis

## 🎨 Example Queries

### Code Analysis
- `"find all database connections and queries"`
- `"analyze error handling patterns"`
- `"locate API endpoints and routing"`
- `"identify security vulnerabilities"`

### Configuration & Setup
- `"find configuration files and settings"`
- `"analyze environment variables"`
- `"locate logging configuration"`

### Data Processing
- `"trace data flow through application"`
- `"find data transformation functions"`
- `"analyze input validation"`

### Testing & Quality
- `"locate test files and coverage"`
- `"find performance bottlenecks"`
- `"analyze code complexity"`

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Install dependencies with `python3 install_deep_research.py`
2. **Permission Errors**: Ensure read access to workspace
3. **Memory Issues**: Use smaller `max_iterations` or `threshold` values
4. **No Results**: Try broader search terms or lower threshold

### Performance Tips

1. **Limit File Count**: Use specific file extensions
2. **Adjust Threshold**: Lower values = more results
3. **Reduce Iterations**: Faster execution with fewer iterations
4. **Cache Results**: Results are cached for repeated searches

## 📈 System Architecture

### LangGraph Workflow
```
Planning → Search → Analysis → Iteration → Synthesis → Report
    ↓        ↓        ↓          ↓           ↓         ↓
  Strategy  Tools   Insights   Follow-up  Combine   Output
```

### State Management
- **ResearchState**: Central state container
- **SearchResult**: Individual result representation
- **ResearchIteration**: Iteration tracking
- **Confidence Scoring**: Quality metrics

### Tool Integration
- **File Tools**: Direct file system access
- **Retrieval Tools**: Advanced search algorithms  
- **Analysis Tools**: Pattern recognition
- **Workflow Nodes**: LangGraph integration

This system provides a comprehensive, intelligent approach to code and document analysis through natural language queries.