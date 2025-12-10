"""
Core workflow engine implementation with WebSocket streaming and background task support
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import uuid
import asyncio
from app.models import (
    GraphDefinition, 
    ExecutionStatus, 
    ExecutionLogEntry,
    ConditionalEdge
)
from app.tools import tool_registry


class WorkflowEngine:
    """Core workflow execution engine with streaming and background execution"""
    
    def __init__(self):
        self.graphs: Dict[str, GraphDefinition] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.background_tasks: Dict[str, asyncio.Task] = {}
    
    def create_graph(self, graph_def: GraphDefinition) -> str:
        """Create a new workflow graph"""
        graph_id = str(uuid.uuid4())
        self.graphs[graph_id] = graph_def
        return graph_id
    
    def get_graph(self, graph_id: str) -> Optional[GraphDefinition]:
        """Retrieve a graph by ID"""
        return self.graphs.get(graph_id)
    
    async def run_graph(
        self, 
        graph_id: str, 
        initial_state: Dict[str, Any],
        stream_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute a workflow graph with optional streaming"""
        graph = self.get_graph(graph_id)
        if not graph:
            raise ValueError(f"Graph {graph_id} not found")
        
        run_id = str(uuid.uuid4())
        
        # Initialize run state
        run_state = {
            "run_id": run_id,
            "graph_id": graph_id,
            "status": ExecutionStatus.RUNNING,
            "current_node": None,
            "state": initial_state.copy(),
            "execution_log": [],
            "start_time": datetime.now()
        }
        
        self.runs[run_id] = run_state
        
        # Send initial status via stream
        if stream_callback:
            await stream_callback({
                "type": "status",
                "run_id": run_id,
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })
        
        try:
            # Execute the workflow
            final_state = await self._execute_workflow(
                graph, 
                run_state["state"], 
                run_state["execution_log"],
                stream_callback,
                run_id
            )
            
            run_state["state"] = final_state
            run_state["status"] = ExecutionStatus.COMPLETED
            run_state["end_time"] = datetime.now()
            
            # Send completion status
            if stream_callback:
                await stream_callback({
                    "type": "status",
                    "run_id": run_id,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            run_state["status"] = ExecutionStatus.FAILED
            run_state["error"] = str(e)
            run_state["end_time"] = datetime.now()
            
            # Send error status
            if stream_callback:
                await stream_callback({
                    "type": "error",
                    "run_id": run_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            raise
        
        return run_state
    
    async def run_graph_background(
        self,
        graph_id: str,
        initial_state: Dict[str, Any]
    ) -> str:
        """Execute a workflow graph as a background task"""
        run_id = str(uuid.uuid4())
        
        # Create background task
        task = asyncio.create_task(
            self.run_graph(graph_id, initial_state)
        )
        
        self.background_tasks[run_id] = task
        
        # Initialize run state immediately
        self.runs[run_id] = {
            "run_id": run_id,
            "graph_id": graph_id,
            "status": ExecutionStatus.PENDING,
            "current_node": None,
            "state": initial_state.copy(),
            "execution_log": [],
            "start_time": datetime.now()
        }
        
        return run_id
    
    async def _execute_workflow(
        self,
        graph: GraphDefinition,
        state: Dict[str, Any],
        execution_log: List[ExecutionLogEntry],
        stream_callback: Optional[Callable] = None,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute workflow nodes in sequence with streaming support"""
        
        # Find the starting node
        current_node = self._find_start_node(graph)
        max_iterations = state.get("max_iterations", 10)
        iteration_count = 0
        
        while current_node and current_node != "END":
            # Update current node in run state
            if run_id and run_id in self.runs:
                self.runs[run_id]["current_node"] = current_node
            
            # Stream node start event
            if stream_callback:
                await stream_callback({
                    "type": "node_start",
                    "node": current_node,
                    "iteration": iteration_count + 1,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Prevent infinite loops
            iteration_count += 1
            if iteration_count > max_iterations:
                log_entry = ExecutionLogEntry(
                    node="SYSTEM",
                    status="terminated",
                    timestamp=datetime.now(),
                    details={"reason": "Max iterations reached"}
                )
                execution_log.append(log_entry)
                
                if stream_callback:
                    await stream_callback({
                        "type": "system",
                        "message": "Max iterations reached",
                        "timestamp": datetime.now().isoformat()
                    })
                break
            
            # Execute current node
            try:
                state = await self._execute_node(
                    graph, 
                    current_node, 
                    state, 
                    execution_log,
                    stream_callback
                )
                
                # Stream node completion
                if stream_callback:
                    await stream_callback({
                        "type": "node_complete",
                        "node": current_node,
                        "state_update": {
                            k: v for k, v in state.items() 
                            if k not in ["code", "max_iterations", "threshold"]
                        },
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Determine next node
                next_node = self._get_next_node(graph, current_node, state)
                
                # Stream transition
                if stream_callback and next_node:
                    await stream_callback({
                        "type": "transition",
                        "from": current_node,
                        "to": next_node,
                        "timestamp": datetime.now().isoformat()
                    })
                
                current_node = next_node
                
            except Exception as e:
                log_entry = ExecutionLogEntry(
                    node=current_node,
                    status="failed",
                    timestamp=datetime.now(),
                    details={"error": str(e)}
                )
                execution_log.append(log_entry)
                
                if stream_callback:
                    await stream_callback({
                        "type": "node_error",
                        "node": current_node,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                raise
        
        return state
    
    def _find_start_node(self, graph: GraphDefinition) -> str:
        """Find the starting node of the workflow"""
        target_nodes = set(graph.edges.values())
        
        for node in graph.nodes.keys():
            if node not in target_nodes:
                return node
        
        return list(graph.nodes.keys())[0] if graph.nodes else None
    
    async def _execute_node(
        self,
        graph: GraphDefinition,
        node_name: str,
        state: Dict[str, Any],
        execution_log: List[ExecutionLogEntry],
        stream_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Execute a single node"""
        
        node_config = graph.nodes.get(node_name)
        if not node_config:
            raise ValueError(f"Node {node_name} not found in graph")
        
        # Get the tool function
        tool_func = tool_registry.get(node_config.function)
        
        # Execute the tool
        start_time = datetime.now()
        
        # Run synchronously in thread pool
        result_state = await asyncio.to_thread(tool_func, state)
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log execution
        log_entry = ExecutionLogEntry(
            node=node_name,
            status="completed",
            timestamp=datetime.now(),
            details={
                "function": node_config.function,
                "duration_ms": duration_ms
            }
        )
        execution_log.append(log_entry)
        
        return result_state
    
    def _get_next_node(
        self,
        graph: GraphDefinition,
        current_node: str,
        state: Dict[str, Any]
    ) -> Optional[str]:
        """Determine the next node to execute"""
        
        # Check for conditional edges first
        if current_node in graph.conditional_edges:
            conditional = graph.conditional_edges[current_node]
            if self._evaluate_condition(conditional.condition, state):
                return conditional.true
            else:
                return conditional.false
        
        # Check regular edges
        if current_node in graph.edges:
            return graph.edges[current_node]
        
        return "END"
    
    def _evaluate_condition(
        self, 
        condition: str, 
        state: Dict[str, Any]
    ) -> bool:
        """Evaluate a conditional expression"""
        try:
            # Replace state variables with their values
            for key, value in state.items():
                if key in condition:
                    condition = condition.replace(key, str(value))
            
            return eval(condition)
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    def get_run_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a workflow run"""
        return self.runs.get(run_id)
    
    def get_background_task_status(self, run_id: str) -> Dict[str, Any]:
        """Get the status of a background task"""
        if run_id not in self.background_tasks:
            return {"status": "not_found"}
        
        task = self.background_tasks[run_id]
        
        if task.done():
            if task.exception():
                return {
                    "status": "failed",
                    "error": str(task.exception())
                }
            return {"status": "completed"}
        
        return {"status": "running"}


# Global engine instance
workflow_engine = WorkflowEngine()
