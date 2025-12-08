# Workflow Engine - AI Engineering Assignment

A minimal workflow/graph engine built with FastAPI that supports nodes, edges, state management, branching, and looping.

## Features

- **Graph Engine**: Define workflows with nodes and edges
- **State Management**: Shared state flows through the workflow
- **Branching**: Conditional routing based on state values
- **Looping**: Repeat nodes until conditions are met
- **Tool Registry**: Register and use Python functions as tools
- **FastAPI Endpoints**: RESTful API for graph management
- **Async Support**: Asynchronous workflow execution
- **Example Workflow**: Code Review Mini-Agent implementation

## Project Structure

```
workflow-engine/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── engine.py            # Core workflow engine
│   ├── tools.py             # Tool registry and implementations
│   └── workflows/
│       ├── __init__.py
│       └── code_review.py   # Code review workflow example
├── requirements.txt
└── README.md
```

## Installation

```bash
# Clone the repository
git clone https://github.com/Tathagt/workflow-engine.git
cd workflow-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## API Endpoints

### 1. Create Graph
```bash
POST /graph/create
```

**Request Body:**
```json
{
  "name": "code_review_workflow",
  "nodes": {
    "extract": {"function": "extract_functions"},
    "analyze": {"function": "check_complexity"},
    "detect": {"function": "detect_issues"},
    "suggest": {"function": "suggest_improvements"},
    "check_quality": {"function": "check_quality_score"}
  },
  "edges": {
    "extract": "analyze",
    "analyze": "detect",
    "detect": "suggest",
    "suggest": "check_quality"
  },
  "conditional_edges": {
    "check_quality": {
      "condition": "quality_score >= threshold",
      "true": "END",
      "false": "analyze"
    }
  }
}
```

**Response:**
```json
{
  "graph_id": "uuid-string",
  "message": "Graph created successfully"
}
```

### 2. Run Graph
```bash
POST /graph/run
```

**Request Body:**
```json
{
  "graph_id": "uuid-string",
  "initial_state": {
    "code": "def example():\n    pass",
    "threshold": 7,
    "max_iterations": 3
  }
}
```

**Response:**
```json
{
  "run_id": "uuid-string",
  "final_state": {
    "code": "...",
    "quality_score": 8,
    "issues": [],
    "suggestions": []
  },
  "execution_log": [
    {"node": "extract", "status": "completed", "timestamp": "..."},
    {"node": "analyze", "status": "completed", "timestamp": "..."}
  ]
}
```

### 3. Get Workflow State
```bash
GET /graph/state/{run_id}
```

**Response:**
```json
{
  "run_id": "uuid-string",
  "status": "completed",
  "current_node": "END",
  "state": {...},
  "execution_log": [...]
}
```

## Example Workflow: Code Review Mini-Agent

The included example implements a code review workflow:

1. **Extract Functions**: Parse code and extract function definitions
2. **Check Complexity**: Analyze cyclomatic complexity
3. **Detect Issues**: Find code smells and basic issues
4. **Suggest Improvements**: Generate improvement suggestions
5. **Check Quality**: Evaluate quality score and loop if needed

### Running the Example

```python
import requests

# Create the code review graph
response = requests.post("http://localhost:8000/graph/create", json={
    "name": "code_review",
    "nodes": {
        "extract": {"function": "extract_functions"},
        "analyze": {"function": "check_complexity"},
        "detect": {"function": "detect_issues"},
        "suggest": {"function": "suggest_improvements"},
        "check_quality": {"function": "check_quality_score"}
    },
    "edges": {
        "extract": "analyze",
        "analyze": "detect",
        "detect": "suggest",
        "suggest": "check_quality"
    },
    "conditional_edges": {
        "check_quality": {
            "condition": "quality_score >= threshold",
            "true": "END",
            "false": "analyze"
        }
    }
})

graph_id = response.json()["graph_id"]

# Run the workflow
code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
"""

response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {
        "code": code,
        "threshold": 7,
        "max_iterations": 3
    }
})

print(response.json())
```

## What the Engine Supports

- ✅ **Nodes**: Python functions that read/modify shared state
- ✅ **State Management**: Dictionary-based state flowing between nodes
- ✅ **Edges**: Simple node-to-node connections
- ✅ **Conditional Branching**: Route based on state conditions
- ✅ **Looping**: Repeat nodes until conditions are met
- ✅ **Tool Registry**: Register and call Python functions
- ✅ **Async Execution**: Non-blocking workflow execution
- ✅ **Execution Logging**: Track workflow progress
- ✅ **In-Memory Storage**: Fast graph and run state storage

## What Could Be Improved With More Time

1. **Persistent Storage**: Use PostgreSQL/SQLite instead of in-memory storage
2. **WebSocket Streaming**: Real-time log streaming for long-running workflows
3. **Parallel Execution**: Run independent nodes concurrently
4. **Error Handling**: More robust error recovery and retry mechanisms
5. **Graph Visualization**: Generate visual representations of workflows
6. **Advanced Branching**: Support multiple conditions and complex routing
7. **Workflow Templates**: Pre-built workflow templates for common use cases
8. **Metrics & Monitoring**: Track execution times, success rates, etc.
9. **Authentication**: API key or JWT-based authentication
10. **Workflow Versioning**: Track and manage different versions of graphs

## Testing

```bash
# Run tests (if implemented)
pytest tests/

# Test with curl
curl -X POST http://localhost:8000/graph/create \
  -H "Content-Type: application/json" \
  -d @examples/code_review_graph.json
```

## Architecture

The engine follows a clean architecture:

- **Models Layer**: Pydantic models for validation
- **Engine Layer**: Core workflow execution logic
- **Tools Layer**: Reusable function registry
- **API Layer**: FastAPI endpoints
- **Workflows Layer**: Example implementations

## License

MIT

## Author

Tathagata Bhattacherjee (tb7595@srmist.edu.in)
