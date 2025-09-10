"""
ROMA - Research-Oriented Multi-Agent system
A LangGraph-based workflow for deep research on local files.
"""

__version__ = "1.0.0"
__author__ = "ROMA Research Agent"
__description__ = "A Python-based LangGraph workflow for deep research on local files"

from .workflows.deep_research_workflow import DeepResearchWorkflow
from .config.settings import Settings

__all__ = ["DeepResearchWorkflow", "Settings"]