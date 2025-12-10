
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class NodeConfig(BaseModel):
    
    function: str
    params: Optional[Dict[str, Any]] = {}


class ConditionalEdge(BaseModel):
    
    condition: str
    true: str
    false: str


class GraphDefinition(BaseModel):
   
    name: str
    nodes: Dict[str, NodeConfig]
    edges: Dict[str, str]
    conditional_edges: Optional[Dict[str, ConditionalEdge]] = {}


class GraphCreateResponse(BaseModel):
   
    graph_id: str
    message: str


class WorkflowState(BaseModel):
    
    data: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        self.data.update(updates)


class ExecutionStatus(str, Enum):
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionLogEntry(BaseModel):
    
    node: str
    status: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class RunRequest(BaseModel):
    
    graph_id: str
    initial_state: Dict[str, Any]


class RunResponse(BaseModel):
    
    run_id: str
    final_state: Dict[str, Any]
    execution_log: List[ExecutionLogEntry]
    status: ExecutionStatus


class StateResponse(BaseModel):
    
    run_id: str
    status: ExecutionStatus
    current_node: Optional[str]
    state: Dict[str, Any]
    execution_log: List[ExecutionLogEntry]
