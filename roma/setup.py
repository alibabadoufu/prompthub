"""
Setup script for ROMA Research Agent.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "langgraph>=0.0.55",
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "langchain-community>=0.0.20",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "typing-extensions>=4.8.0",
        "chardet>=5.2.0",
        "python-magic>=0.4.27",
        "PyPDF2>=3.0.1",
        "python-docx>=0.8.11",
        "openpyxl>=3.1.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "markdown>=3.5.0",
        "pyyaml>=6.0.1",
        "requests>=2.31.0",
        "aiofiles>=23.2.0"
    ]

setup(
    name="roma-research-agent",
    version="1.0.0",
    author="ROMA Research Team",
    author_email="research@roma-agent.com",
    description="A Python-based LangGraph workflow for deep research on local files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roma-research/roma-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "roma=roma.main:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "roma": [
            "config/*.yaml",
            "config/*.yml",
            "config/*.json",
        ],
    },
    keywords="research, analysis, langgraph, nlp, file-processing, ai, workflow",
    project_urls={
        "Bug Reports": "https://github.com/roma-research/roma-agent/issues",
        "Source": "https://github.com/roma-research/roma-agent",
        "Documentation": "https://roma-research.readthedocs.io/",
    },
)