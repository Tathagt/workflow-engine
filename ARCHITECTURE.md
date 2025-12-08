# Architecture Documentation

## Overview

This workflow engine is designed with a clean, modular architecture that separates concerns and makes the codebase easy to understand and extend.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         FastAPI Layer (main.py)         │
│  - HTTP endpoints                       │
│  - Request/Response handling            │
│  - Input validation                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Models Layer (models.py)           │
│  - Pydantic models                      │
│  - Data validation                      │
│  - Type definitions                     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Engine Layer (engine.py)          │
│  - Workflow execution logic             │
│  - State management                     │
│  - Node traversal                       │
│  - Conditional routing                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Tools Layer (tools.py)            │
│  - Tool registry                        │
│  - Tool implementations                 │
│  - Function execution                   │
└─────────────────────────────────────────┘
```

## Core Components

### 1. FastAPI Application (`app/main.py`)

**Responsibilities:**
- Expose REST API endpoints
- Handle HTTP requests/responses
- Validate input data
- Return appropriate status codes

**Key Endpoints:**
- `POST /graph/create` - Create workflow graphs
- `POST /graph/run` - Execute workflows
- `GET /graph/state/{run_id}` - Query execution state

### 2. Workflow Engine (`app/engine.py`)

**Responsibilities:**
- Manage workflow graphs
- Execute nodes in sequence
- Handle state transitions
- Evaluate conditional branches
- Implement loop detection

**Key Classes:**
- `WorkflowEngine` - Main engine class
  - `create_graph()` - Store graph definitions
  - `run_graph()` - Execute workflows asynchronously
  - `_execute_workflow()` - Core execution loop
  - `_execute_node()` - Run individual nodes
  - `_get_next_node()` - Determine next node
  - `_evaluate_condition()` - Evaluate branch conditions

**Execution Flow:**
```
1. Find start node
2. Execute node function
3. Update state
4. Log execution
5. Evaluate conditions
6. Determine next node
7. Repeat until END or max iterations
```

### 3. Tool Registry (`app/tools.py`)

**Responsibilities:**
- Register callable functions
- Provide function lookup
- Implement domain-specific tools

**Key Classes:**
- `ToolRegistry` - Function registry
  - `register()` - Add new tools
  - `get()` - Retrieve tools by name
  - `list_tools()` - List all tools

**Registered Tools:**
- `extract_functions` - Parse code and extract functions
- `check_complexity` - Analyze cyclomatic complexity
- `detect_issues` - Find code smells
- `suggest_improvements` - Generate suggestions
- `check_quality_score` - Calculate quality metrics

### 4. Data Models (`app/models.py`)

**Responsibilities:**
- Define data structures
- Validate input/output
- Provide type safety

**Key Models:**
- `GraphDefinition` - Workflow graph structure
- `NodeConfig` - Node configuration
- `ConditionalEdge` - Branch conditions
- `WorkflowState` - State container
- `ExecutionLogEntry` - Execution tracking
- `RunRequest/Response` - API contracts

## Data Flow

### Graph Creation Flow
```
Client Request
    ↓
FastAPI Endpoint
    ↓
Pydantic Validation
    ↓
WorkflowEngine.create_graph()
    ↓
Store in memory
    ↓
Return graph_id
```

### Workflow Execution Flow
```
Client Request (graph_id + initial_state)
    ↓
FastAPI Endpoint
    ↓
WorkflowEngine.run_graph()
    ↓
Initialize run state
    ↓
Execute workflow loop:
  - Get current node
  - Fetch tool function
  - Execute function with state
  - Update state
  - Log execution
  - Evaluate conditions
  - Get next node
    ↓
Return final state + logs
```

## State Management

The workflow state is a simple dictionary that flows through nodes:

```python
state = {
    "code": "...",           # Input data
    "functions": [...],      # Extracted data
    "issues": [...],         # Analysis results
    "quality_score": 8.5,    # Computed metrics
    "iteration": 2,          # Loop counter
    "threshold": 7,          # Configuration
    "max_iterations": 3      # Safety limit
}
```

Each node:
1. Receives the current state
2. Performs its operation
3. Updates the state
4. Returns the modified state

## Branching and Looping

### Conditional Branching

Conditional edges evaluate expressions against the state:

```python
{
    "check_quality": {
        "condition": "quality_score >= threshold",
        "true": "END",
        "false": "analyze"
    }
}
```

The engine:
1. Evaluates the condition
2. Routes to `true` or `false` node
3. Continues execution

### Loop Detection

Loops are implemented via conditional edges that route back to earlier nodes:

```
analyze → detect → suggest → check_quality
   ↑                              ↓
   └──────────────────────────────┘
         (if quality_score < threshold)
```

Safety mechanisms:
- `max_iterations` parameter
- Iteration counter in state
- Automatic termination

## Async Execution

The engine uses Python's `asyncio` for non-blocking execution:

```python
async def run_graph(self, graph_id, initial_state):
    # Async execution allows concurrent workflows
    final_state = await self._execute_workflow(...)
    return final_state
```

Benefits:
- Non-blocking API responses
- Concurrent workflow execution
- Better resource utilization

## Storage

Currently uses in-memory storage:

```python
self.graphs: Dict[str, GraphDefinition] = {}
self.runs: Dict[str, Dict[str, Any]] = {}
```

**Advantages:**
- Fast access
- Simple implementation
- No external dependencies

**Limitations:**
- Data lost on restart
- Not suitable for production
- No persistence

**Future Enhancement:**
Replace with PostgreSQL/SQLite for persistence.

## Error Handling

The engine implements multiple error handling strategies:

1. **Validation Errors** - Caught by Pydantic
2. **Execution Errors** - Logged and propagated
3. **Timeout Protection** - Max iterations limit
4. **Graceful Degradation** - Fallback to regex if AST fails

## Extension Points

The architecture is designed for easy extension:

### Adding New Tools

```python
def my_custom_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    # Your logic here
    state["result"] = "processed"
    return state

tool_registry.register("my_custom_tool", my_custom_tool)
```

### Adding New Workflows

```python
CUSTOM_WORKFLOW = {
    "name": "my_workflow",
    "nodes": {...},
    "edges": {...},
    "conditional_edges": {...}
}
```

### Adding Persistence

Replace in-memory storage with database:

```python
class DatabaseEngine(WorkflowEngine):
    def create_graph(self, graph_def):
        graph_id = str(uuid.uuid4())
        db.save_graph(graph_id, graph_def)
        return graph_id
```

## Design Principles

1. **Separation of Concerns** - Each layer has a single responsibility
2. **Type Safety** - Pydantic models ensure data validity
3. **Extensibility** - Easy to add new tools and workflows
4. **Simplicity** - Clean, readable code over complexity
5. **Async-First** - Non-blocking execution by default

## Performance Considerations

- **In-Memory Storage** - Fast but not persistent
- **Synchronous Tools** - Tools run in thread pool
- **No Caching** - Each execution is independent
- **No Parallelization** - Nodes execute sequentially

## Security Considerations

- **Code Execution** - `eval()` used for conditions (limited scope)
- **Input Validation** - Pydantic validates all inputs
- **No Authentication** - Open API (add auth for production)
- **Rate Limiting** - Not implemented (add for production)

## Testing Strategy

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test full workflows
3. **Example Scripts** - Demonstrate usage
4. **Manual Testing** - Use FastAPI docs UI

## Future Enhancements

1. **Persistent Storage** - PostgreSQL/SQLite
2. **WebSocket Streaming** - Real-time logs
3. **Parallel Execution** - Run independent nodes concurrently
4. **Graph Visualization** - Generate diagrams
5. **Workflow Templates** - Pre-built workflows
6. **Metrics Dashboard** - Execution analytics
7. **Authentication** - API security
8. **Rate Limiting** - Prevent abuse
9. **Caching** - Optimize repeated executions
10. **Distributed Execution** - Scale across machines
