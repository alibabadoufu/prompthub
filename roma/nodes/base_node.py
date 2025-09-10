"""
Base node class for all workflow nodes in the ROMA research agent.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class NodeState:
    """Represents the state passed between nodes."""
    # Input parameters
    directory_path: Optional[str] = None
    file_patterns: Optional[list] = None
    query: Optional[str] = None
    query_keywords: Optional[list] = None
    research_depth: str = "medium"
    max_results: int = 50
    
    # Processing state
    discovered_files: Optional[list] = None
    extracted_content: Optional[list] = None
    analyzed_content: Optional[list] = None
    research_findings: Optional[list] = None
    final_report: Optional[str] = None
    
    # Metadata
    processing_start_time: Optional[datetime] = None
    processing_end_time: Optional[datetime] = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    node_history: list = field(default_factory=list)
    
    def add_error(self, error: str, node_name: str = "unknown"):
        """Add an error to the state."""
        self.errors.append({
            "error": error,
            "node": node_name,
            "timestamp": datetime.now()
        })
        logger.error(f"Node {node_name}: {error}")
    
    def add_warning(self, warning: str, node_name: str = "unknown"):
        """Add a warning to the state."""
        self.warnings.append({
            "warning": warning,
            "node": node_name,
            "timestamp": datetime.now()
        })
        logger.warning(f"Node {node_name}: {warning}")
    
    def add_node_execution(self, node_name: str, execution_time: float, success: bool):
        """Record node execution in history."""
        self.node_history.append({
            "node": node_name,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now()
        })


class BaseNode(ABC):
    """Base class for all workflow nodes."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def process(self, state: NodeState) -> NodeState:
        """
        Process the node with the given state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        pass
    
    async def execute(self, state: NodeState) -> NodeState:
        """
        Execute the node with error handling and timing.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        start_time = datetime.now()
        success = False
        
        try:
            self.logger.info(f"Starting execution of {self.name}")
            
            # Validate input state
            validation_error = self.validate_input(state)
            if validation_error:
                state.add_error(validation_error, self.name)
                return state
            
            # Process the node
            updated_state = await self.process(state)
            
            # Validate output state
            validation_error = self.validate_output(updated_state)
            if validation_error:
                updated_state.add_warning(validation_error, self.name)
            
            success = True
            self.logger.info(f"Successfully completed execution of {self.name}")
            return updated_state
            
        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            state.add_error(error_msg, self.name)
            self.logger.error(error_msg, exc_info=True)
            return state
            
        finally:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            state.add_node_execution(self.name, execution_time, success)
    
    def validate_input(self, state: NodeState) -> Optional[str]:
        """
        Validate input state for the node.
        
        Args:
            state: Input state
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Default implementation - override in subclasses
        return None
    
    def validate_output(self, state: NodeState) -> Optional[str]:
        """
        Validate output state from the node.
        
        Args:
            state: Output state
            
        Returns:
            Warning message if validation has concerns, None otherwise
        """
        # Default implementation - override in subclasses
        return None
    
    def get_node_info(self) -> Dict[str, Any]:
        """
        Get information about this node.
        
        Returns:
            Node information dictionary
        """
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "description": self.__doc__ or "No description available"
        }