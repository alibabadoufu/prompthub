# Deep Research LangGraph Workflow

A comprehensive intelligent system for performing deep research on local files using LangGraph. This system can analyze codebases, documentation, and other file collections to answer complex questions through iterative search and analysis.

## 🌟 Features

### Advanced Search Capabilities
- **Grep Search**: Pattern-based text search with context
- **Fuzzy Search**: Approximate matching for flexible queries
- **Regex Search**: Complex pattern matching
- **Code Structure Analysis**: Function, class, and import detection
- **Configuration File Search**: Specialized config file analysis
- **Data Flow Analysis**: Data processing pattern detection

### Retrieval Methods
- **Dense Retrieval**: TF-IDF based semantic search
- **BM25 Retrieval**: Statistical ranking algorithm
- **Hybrid Retrieval**: Combined dense and sparse methods

### Intelligent Workflow
- **Iterative Research**: Multi-step investigation with follow-up queries
- **Content Analysis**: Pattern recognition and insight extraction
- **Confidence Scoring**: Research quality assessment
- **Comprehensive Reporting**: Detailed analysis reports

## 🏗️ Architecture

```
deep_research/
├── __init__.py
├── __main__.py
├── main.py                 # CLI entry point
├── models/
│   ├── __init__.py
│   └── state.py           # State management
├── tools/
│   ├── __init__.py
│   ├── file_tools.py      # File search and analysis
│   ├── retrieval_tools.py # Advanced retrieval methods
│   └── analysis_tools.py  # Content analysis and patterns
├── nodes/
│   ├── __init__.py
│   └── research_nodes.py  # LangGraph workflow nodes
├── workflows/
│   ├── __init__.py
│   └── research_workflow.py # Main workflow orchestration
└── utils/
    ├── __init__.py
    └── helpers.py         # Utility functions
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install specific deep research dependencies
pip install langgraph langchain langchain-core numpy pathlib2
```

### Basic Usage

```bash
# Basic research query
python -m deep_research.main "find authentication code" --workspace /path/to/project

# Advanced research with custom settings
python -m deep_research.main "data processing pipeline" \
  --workspace /path/to/project \
  --max-iterations 5 \
  --threshold 0.5 \
  --output results.json \
  --format json

# Interactive mode
python -m deep_research.main --interactive --workspace /path/to/project
```

### Python API

```python
from deep_research.workflows.research_workflow import DeepResearchWorkflow

# Initialize workflow
workflow = DeepResearchWorkflow(
    workspace_path="/path/to/project",
    max_iterations=3,
    similarity_threshold=0.3
)

# Run research
results = workflow.run_research("find database connections")

# Access results
print(f"Confidence: {results['confidence_score']}")
print(f"Total results: {results['total_results']}")
for insight in results['key_insights']:
    print(f"- {insight}")
```

## 🔄 Workflow Process

1. **Planning**: Analyze workspace and plan search strategies
2. **Search**: Execute multiple search methods (grep, retrieval, etc.)
3. **Analysis**: Extract insights and patterns from results
4. **Iteration**: Generate follow-up queries for deeper investigation
5. **Synthesis**: Combine findings and calculate confidence scores
6. **Report**: Generate comprehensive research report

## 🛠️ Configuration Options

### Command Line Options

- `--workspace, -w`: Path to workspace (required)
- `--max-iterations, -i`: Maximum research iterations (default: 3)
- `--threshold, -t`: Similarity threshold (default: 0.3)
- `--output, -o`: Output file path
- `--format, -f`: Output format (json, markdown, text)
- `--interactive`: Run in interactive mode
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Configuration File

```yaml
# config.yaml
max_iterations: 5
similarity_threshold: 0.4
search_strategies:
  - grep_search
  - fuzzy_search
  - dense_retrieval
  - bm25_retrieval
```

## 📊 Output Formats

### JSON Output
```json
{
  "query": "find authentication code",
  "status": "completed",
  "confidence_score": 0.85,
  "total_results": 42,
  "key_insights": [
    "Authentication logic found in auth.py",
    "JWT token handling in utils.py"
  ],
  "top_results": [...],
  "research_report": "# Deep Research Report..."
}
```

### Markdown Report
```markdown
# Deep Research Report
**Query:** find authentication code
**Confidence Score:** 0.85/1.0

## Key Insights
1. Authentication logic found in auth.py
2. JWT token handling in utils.py

## Most Relevant Findings
### 1. auth.py
**Relevance:** 0.95
**Content:** def authenticate_user(username, password)...
```

## 🎯 Use Cases

### Code Analysis
```bash
# Find specific functionality
python -m deep_research.main "error handling patterns" --workspace ./src

# Analyze data flow
python -m deep_research.main "database queries and connections" --workspace ./

# Security analysis
python -m deep_research.main "authentication and authorization" --workspace ./
```

### Documentation Research
```bash
# API documentation
python -m deep_research.main "API endpoints and routes" --workspace ./docs

# Configuration analysis
python -m deep_research.main "environment variables and config" --workspace ./
```

### Debugging and Investigation
```bash
# Bug investigation
python -m deep_research.main "memory leaks or performance issues" --workspace ./

# Dependency analysis
python -m deep_research.main "external library usage" --workspace ./
```

## 🧪 Demo

Run the included demo to see the system in action:

```bash
# Automated demo with sample queries
python deep_research_demo.py

# Interactive demo
python deep_research_demo.py --interactive
```

## 🔧 Advanced Features

### Custom Search Strategies
The system automatically selects appropriate search strategies based on query content:

- **Code-related queries**: Activates code structure analysis
- **Configuration queries**: Focuses on config files
- **Data processing queries**: Enables data flow analysis
- **Complex queries**: Uses advanced retrieval methods

### Iterative Research
The system can perform multiple research iterations:

1. Initial broad search
2. Analysis of results and insight extraction
3. Generation of follow-up questions
4. Focused follow-up searches
5. Synthesis of all findings

### Content Analysis
Advanced content analysis includes:

- Pattern recognition across files
- Code structure analysis
- Relationship discovery
- Theme identification
- Statistical analysis

## 🤝 Contributing

The system is designed to be extensible:

1. **Add new search tools**: Implement in `tools/`
2. **Create custom nodes**: Add to `nodes/`
3. **Extend analysis**: Enhance `analysis_tools.py`
4. **Custom workflows**: Modify `research_workflow.py`

## 📝 License

This project follows the same license as the parent project.

## 🔍 Examples

### Research Query Examples

- `"find all database connections and queries"`
- `"analyze error handling patterns"`
- `"locate configuration files and settings"`
- `"identify security vulnerabilities"`
- `"trace data flow through the application"`
- `"find API endpoints and routing logic"`
- `"analyze test coverage and patterns"`
- `"locate logging and monitoring code"`

### Interactive Session Example

```
🔍 Enter research query: find authentication methods

🚀 Researching: find authentication methods
📊 Research Complete!
  - Status: completed
  - Confidence: 0.78
  - Results: 15
  - Files: 8

💡 Key Insights:
  1. Authentication logic found in auth.py
  2. JWT token handling in middleware
  3. Password hashing uses bcrypt

🎯 Top Results:
  1. auth.py (Score: 0.92)
  2. middleware.py (Score: 0.85)
  3. utils.py (Score: 0.73)
```

This deep research system provides a powerful, intelligent way to explore and understand complex codebases and file collections through natural language queries.