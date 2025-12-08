"""
Pydantic models for workflow engine
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class NodeConfig(BaseModel):
    """Configuration for a workflow node"""
    function: str
    params: Optional[Dict[str, Any]] = {}


class ConditionalEdge(BaseModel):
    """Configuration for conditional routing"""
    condition: str
    true: str
    false: str


class GraphDefinition(BaseModel):
    """Definition of a workflow graph"""
    name: str
    nodes: Dict[str, NodeConfig]
    edges: Dict[str, str]
    conditional_edges: Optional[Dict[str, ConditionalEdge]] = {}


class GraphCreateResponse(BaseModel):
    """Response for graph creation"""
    graph_id: str
    message: str


class WorkflowState(BaseModel):
    """State that flows through the workflow"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        self.data.update(updates)


class ExecutionStatus(str, Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionLogEntry(BaseModel):
    """Single entry in execution log"""
    node: str
    status: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class RunRequest(BaseModel):
    """Request to run a workflow"""
    graph_id: str
    initial_state: Dict[str, Any]


class RunResponse(BaseModel):
    """Response from workflow execution"""
    run_id: str
    final_state: Dict[str, Any]
    execution_log: List[ExecutionLogEntry]
    status: ExecutionStatus


class StateResponse(BaseModel):
    """Response for state query"""
    run_id: str
    status: ExecutionStatus
    current_node: Optional[str]
    state: Dict[str, Any]
    execution_log: List[ExecutionLogEntry]
