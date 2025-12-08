"""
Core workflow engine implementation
"""
from typing import Dict, Any, Optional, List
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
    """Core workflow execution engine"""
    
    def __init__(self):
        self.graphs: Dict[str, GraphDefinition] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
    
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
        initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow graph"""
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
        
        try:
            # Execute the workflow
            final_state = await self._execute_workflow(
                graph, 
                run_state["state"], 
                run_state["execution_log"]
            )
            
            run_state["state"] = final_state
            run_state["status"] = ExecutionStatus.COMPLETED
            run_state["end_time"] = datetime.now()
            
        except Exception as e:
            run_state["status"] = ExecutionStatus.FAILED
            run_state["error"] = str(e)
            run_state["end_time"] = datetime.now()
            raise
        
        return run_state
    
    async def _execute_workflow(
        self,
        graph: GraphDefinition,
        state: Dict[str, Any],
        execution_log: List[ExecutionLogEntry]
    ) -> Dict[str, Any]:
        """Execute workflow nodes in sequence"""
        
        # Find the starting node (first node in edges or first node defined)
        current_node = self._find_start_node(graph)
        visited_nodes = set()
        max_iterations = state.get("max_iterations", 10)
        iteration_count = 0
        
        while current_node and current_node != "END":
            # Prevent infinite loops
            iteration_count += 1
            if iteration_count > max_iterations:
                execution_log.append(ExecutionLogEntry(
                    node="SYSTEM",
                    status="terminated",
                    timestamp=datetime.now(),
                    details={"reason": "Max iterations reached"}
                ))
                break
            
            # Execute current node
            try:
                state = await self._execute_node(
                    graph, 
                    current_node, 
                    state, 
                    execution_log
                )
                
                # Determine next node
                current_node = self._get_next_node(
                    graph, 
                    current_node, 
                    state
                )
                
            except Exception as e:
                execution_log.append(ExecutionLogEntry(
                    node=current_node,
                    status="failed",
                    timestamp=datetime.now(),
                    details={"error": str(e)}
                ))
                raise
        
        return state
    
    def _find_start_node(self, graph: GraphDefinition) -> str:
        """Find the starting node of the workflow"""
        # The start node is one that is not a target of any edge
        target_nodes = set(graph.edges.values())
        
        for node in graph.nodes.keys():
            if node not in target_nodes:
                return node
        
        # If all nodes are targets, return the first one
        return list(graph.nodes.keys())[0] if graph.nodes else None
    
    async def _execute_node(
        self,
        graph: GraphDefinition,
        node_name: str,
        state: Dict[str, Any],
        execution_log: List[ExecutionLogEntry]
    ) -> Dict[str, Any]:
        """Execute a single node"""
        
        node_config = graph.nodes.get(node_name)
        if not node_config:
            raise ValueError(f"Node {node_name} not found in graph")
        
        # Get the tool function
        tool_func = tool_registry.get(node_config.function)
        
        # Execute the tool
        start_time = datetime.now()
        
        # Run synchronously (can be made async if tools are async)
        result_state = await asyncio.to_thread(tool_func, state)
        
        # Log execution
        execution_log.append(ExecutionLogEntry(
            node=node_name,
            status="completed",
            timestamp=datetime.now(),
            details={
                "function": node_config.function,
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
            }
        ))
        
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
        
        # No more nodes
        return "END"
    
    def _evaluate_condition(
        self, 
        condition: str, 
        state: Dict[str, Any]
    ) -> bool:
        """Evaluate a conditional expression"""
        
        # Simple condition evaluation
        # Format: "key operator value" (e.g., "quality_score >= threshold")
        try:
            # Replace state variables with their values
            for key, value in state.items():
                if key in condition:
                    condition = condition.replace(key, str(value))
            
            # Evaluate the condition
            return eval(condition)
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    def get_run_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a workflow run"""
        return self.runs.get(run_id)


# Global engine instance
workflow_engine = WorkflowEngine()
