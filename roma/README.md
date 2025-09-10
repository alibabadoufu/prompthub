# ROMA Research Agent

A Python-based LangGraph workflow for deep research on local files.

## Overview

ROMA (Research-Oriented Multi-Agent) is a sophisticated research agent built using LangGraph that can perform comprehensive analysis on local file systems. It discovers, extracts, analyzes, and generates detailed research reports from various file types including text documents, code files, PDFs, and more.

## Features

- **Multi-format File Support**: Handles text files, documents (PDF, DOCX, XLSX), code files, and more
- **Intelligent Content Extraction**: Uses specialized parsers for different file types
- **Deep Analysis**: Extracts keywords, entities, relationships, and patterns from content
- **Flexible Research Queries**: Support for both natural language queries and keyword-based searches
- **Comprehensive Reporting**: Generates detailed research reports with statistics and findings
- **Configurable Workflow**: Customizable processing parameters and output formats
- **Async Processing**: Efficient concurrent processing of multiple files
- **LangGraph Integration**: Built on LangGraph for robust workflow orchestration

## Installation

### From Source

```bash
git clone https://github.com/roma-research/roma-agent.git
cd roma-agent
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/roma-research/roma-agent.git
cd roma-agent
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Basic research on current directory
roma --directory . --query "machine learning algorithms"

# Research with specific keywords and file types
roma --directory ./src --keywords "python" "flask" "api" --patterns "*.py"

# Deep research with custom output
roma --directory ./docs --query "installation guide" --depth deep --output report.md

# JSON output for programmatic use
roma --directory . --query "database" --json-output --output results.json
```

### Python API Usage

```python
import asyncio
from roma import DeepResearchWorkflow

async def main():
    # Create workflow
    workflow = DeepResearchWorkflow()
    
    # Run research
    results = await workflow.run_research(
        directory_path="./my_project",
        query="API documentation and examples",
        research_depth="deep",
        max_results=100
    )
    
    # Access results
    print(f"Found {len(results['findings'])} research findings")
    print(results['report'])

asyncio.run(main())
```

## Architecture

ROMA follows a modular architecture with the following components:

### Nodes (Processing Units)
- **FileDiscoveryNode**: Discovers and filters files for processing
- **ContentExtractionNode**: Extracts content from various file formats
- **AnalysisNode**: Analyzes content for patterns, keywords, and insights
- **ResearchNode**: Executes research queries on analyzed content
- **ReportGenerationNode**: Generates comprehensive research reports

### Tools (Utilities)
- **FileHandler**: File operations and type detection
- **DocumentParser**: Specialized parsers for different document formats
- **TextProcessor**: Text preprocessing and tokenization
- **TextAnalyzer**: Advanced text analysis and pattern recognition
- **ResearchTool**: Research query execution and finding generation

### Workflow
The LangGraph workflow orchestrates the entire research process:

```
File Discovery → Content Extraction → Analysis → Research → Report Generation
```

## Configuration

ROMA can be configured using YAML or JSON configuration files:

```yaml
# roma_config.yaml
workflow:
  max_concurrent_files: 10
  max_concurrent_analysis: 5
  research_depth: "medium"
  max_results: 50

file_processing:
  max_file_size_mb: 100
  supported_extensions:
    - ".txt"
    - ".md"
    - ".py"
    - ".pdf"
    - ".docx"
  exclude_patterns:
    - "*.pyc"
    - "__pycache__/*"
    - ".git/*"

analysis:
  min_keyword_length: 3
  max_keywords_per_file: 20
  chunk_size: 1000

research:
  min_confidence_threshold: 0.1
  enable_entity_extraction: true
```

## Supported File Types

### Text Files
- `.txt`, `.md`, `.rst`, `.log`
- Source code: `.py`, `.js`, `.java`, `.cpp`, `.c`, `.h`
- Web files: `.html`, `.css`, `.xml`
- Configuration: `.json`, `.yaml`, `.yml`
- Data files: `.csv`, `.sql`

### Document Files
- PDF: `.pdf`
- Microsoft Office: `.docx`, `.xlsx`, `.pptx`
- OpenDocument: `.odt`, `.ods`

## Research Capabilities

### Content Analysis
- Keyword extraction and frequency analysis
- Entity recognition (organizations, technologies, etc.)
- Relationship extraction between concepts
- Process and workflow identification
- Code snippet and function detection
- Definition and explanation extraction

### Query Types
- **Natural Language Queries**: "Find documentation about API authentication"
- **Keyword Searches**: Multiple keywords with relevance scoring
- **Pattern Matching**: Regular expression and pattern-based searches
- **Category Filtering**: Filter by content categories (technical, business, etc.)

### Research Depths
- **Shallow**: Basic keyword matching and simple analysis
- **Medium**: Comprehensive analysis with entity extraction
- **Deep**: Advanced pattern recognition and relationship analysis

## Output Formats

### Text Report
Comprehensive markdown report with:
- Executive summary
- Processing statistics
- Detailed findings by category
- Source file references
- Processing timeline and errors

### JSON Output
Structured data format with:
- Research findings with confidence scores
- Processing statistics
- Error and warning information
- Metadata and configuration used

## Examples

### Research Code Documentation
```bash
roma --directory ./src --query "API endpoints and authentication" --patterns "*.py" "*.md"
```

### Analyze Project Structure
```bash
roma --directory . --keywords "architecture" "design" "structure" --depth deep
```

### Find Configuration Information
```bash
roma --directory ./config --query "database configuration and connection strings"
```

### Generate JSON Report
```bash
roma --directory ./docs --query "installation guide" --json-output --output analysis.json
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black roma/
```

### Type Checking
```bash
mypy roma/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Uses [LangChain](https://github.com/langchain-ai/langchain) ecosystem for AI capabilities
- Inspired by research automation and knowledge discovery workflows

## Support

- Documentation: [https://roma-research.readthedocs.io/](https://roma-research.readthedocs.io/)
- Issues: [https://github.com/roma-research/roma-agent/issues](https://github.com/roma-research/roma-agent/issues)
- Discussions: [https://github.com/roma-research/roma-agent/discussions](https://github.com/roma-research/roma-agent/discussions)