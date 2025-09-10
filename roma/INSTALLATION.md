# ROMA Research Agent - Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for development installation)

## Installation Methods

### Method 1: Development Installation (Recommended)

1. **Clone or copy the ROMA directory**:
   ```bash
   # If you have the roma folder locally
   cd /path/to/roma
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Install development dependencies** (optional):
   ```bash
   pip install -e ".[dev]"
   ```

### Method 2: Direct Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add to Python path** (if not using pip install):
   ```bash
   export PYTHONPATH="/path/to/roma:$PYTHONPATH"
   ```

## Verify Installation

### Quick Test
```bash
# Test CLI interface
python -m roma.main --version

# Or if installed with pip
roma --version
```

### Run Demo
```bash
# From the roma directory
python demo.py
```

### Run Unit Tests
```bash
# Install test dependencies first
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## Configuration

### Default Configuration
ROMA works out of the box with default settings. Configuration files are located in:
- `config/default_config.yaml` - Default settings
- `roma_config.yaml` - Optional user configuration (create in your working directory)

### Custom Configuration
Create a `roma_config.yaml` file in your working directory:

```yaml
workflow:
  max_concurrent_files: 5
  research_depth: "deep"
  max_results: 100

logging:
  level: "DEBUG"
  log_file: "roma.log"

file_processing:
  max_file_size_mb: 50
  exclude_patterns:
    - "*.pyc"
    - "__pycache__/*"
    - ".git/*"
    - "node_modules/*"
```

## Usage Examples

### Command Line Interface

```bash
# Basic research
roma --directory . --query "machine learning algorithms"

# With specific keywords
roma --directory ./src --keywords "python" "api" "database"

# Deep analysis with output file
roma --directory ./docs --query "installation guide" --depth deep --output report.md

# JSON output
roma --directory . --query "configuration" --json-output --output results.json
```

### Python API

```python
import asyncio
from roma import DeepResearchWorkflow

async def main():
    workflow = DeepResearchWorkflow()
    
    results = await workflow.run_research(
        directory_path="./my_project",
        query="API documentation and examples",
        research_depth="medium",
        max_results=50
    )
    
    print(f"Found {len(results['findings'])} findings")
    print(results['report'])

asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'langgraph'**
   ```bash
   pip install langgraph langchain langchain-core
   ```

2. **Magic library not found (for file type detection)**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install libmagic1
   
   # On macOS
   brew install libmagic
   
   # On Windows
   pip install python-magic-bin
   ```

3. **PDF parsing issues**
   ```bash
   pip install PyPDF2
   ```

4. **Document parsing issues**
   ```bash
   pip install python-docx openpyxl
   ```

### Performance Optimization

1. **Reduce concurrent processing** for limited resources:
   ```yaml
   workflow:
     max_concurrent_files: 3
     max_concurrent_analysis: 2
   ```

2. **Limit file size** for faster processing:
   ```yaml
   file_processing:
     max_file_size_mb: 10
   ```

3. **Use file patterns** to focus on specific types:
   ```bash
   roma --directory . --query "documentation" --patterns "*.md" "*.txt"
   ```

### Logging and Debugging

1. **Enable debug logging**:
   ```bash
   roma --directory . --query "test" --log-level DEBUG
   ```

2. **Save logs to file**:
   ```bash
   roma --directory . --query "test" --log-file debug.log
   ```

3. **Check configuration**:
   ```python
   from roma.config.settings import get_settings
   settings = get_settings()
   print(settings.to_dict())
   ```

## System Requirements

### Minimum Requirements
- **RAM**: 2GB available memory
- **Storage**: 100MB for installation + space for processing files
- **CPU**: Any modern CPU (single-core sufficient for small datasets)

### Recommended Requirements
- **RAM**: 4GB+ for processing large document collections
- **Storage**: 1GB+ for caching and temporary files
- **CPU**: Multi-core CPU for optimal concurrent processing

### Supported Platforms
- **Linux**: All major distributions (Ubuntu, CentOS, Debian, etc.)
- **macOS**: 10.14+ (Mojave and newer)
- **Windows**: Windows 10/11 (with Python 3.8+)

## File Type Support

### Fully Supported
- **Text**: .txt, .md, .rst, .log
- **Code**: .py, .js, .java, .cpp, .c, .h, .php, .rb, .go
- **Web**: .html, .css, .xml
- **Config**: .json, .yaml, .yml
- **Data**: .csv

### Document Support (requires additional libraries)
- **PDF**: .pdf (requires PyPDF2)
- **Office**: .docx, .xlsx (requires python-docx, openpyxl)

### Adding New File Types

To add support for new file types, extend the `DocumentParser` class in `tools/document_parser.py`:

```python
async def _parse_custom_format(self, file_path: Path) -> Dict[str, Any]:
    """Parse custom file format."""
    # Implementation here
    pass
```

## Getting Help

1. **Check the README**: Comprehensive documentation in `README.md`
2. **Run the demo**: `python demo.py` for examples
3. **Check logs**: Enable debug logging to see detailed processing information
4. **Review configuration**: Ensure settings match your requirements

## Next Steps

1. **Try the demo**: Run `python demo.py` to see ROMA in action
2. **Analyze your files**: Start with a small directory to test functionality
3. **Customize configuration**: Adjust settings based on your needs
4. **Explore API**: Use the Python API for integration with your applications