# Quick Start Guide

Get up and running with the Workflow Engine in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

```bash
# Clone the repository
git clone https://github.com/Tathagt/workflow-engine.git
cd workflow-engine

# Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Start the Server

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Test the API

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Run the Example

In a new terminal (keep the server running):

```bash
# Activate the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the test script
python examples/test_workflow.py
```

You should see output showing:
- Graph creation
- Workflow execution
- Code analysis results
- Quality scores
- Execution logs

## Using the API

### 1. Create a Workflow Graph

```bash
curl -X POST http://localhost:8000/graph/create \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

Response:
```json
{
  "graph_id": "abc-123-def-456",
  "message": "Graph created successfully"
}
```

### 2. Run the Workflow

```bash
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "abc-123-def-456",
    "initial_state": {
      "code": "def hello():\n    print(\"Hello World\")",
      "threshold": 7,
      "max_iterations": 3
    }
  }'
```

### 3. Check Workflow State

```bash
curl http://localhost:8000/graph/state/{run_id}
```

## Using the Interactive API Docs

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response below

## Example Code (Python)

```python
import requests

# Create graph
response = requests.post("http://localhost:8000/graph/create", json={
    "name": "my_workflow",
    "nodes": {
        "step1": {"function": "extract_functions"},
        "step2": {"function": "check_complexity"}
    },
    "edges": {
        "step1": "step2"
    }
})

graph_id = response.json()["graph_id"]

# Run workflow
response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {
        "code": "def test(): pass",
        "threshold": 7
    }
})

result = response.json()
print(f"Quality Score: {result['final_state']['quality_score']}")
```

## Understanding the Code Review Workflow

The example workflow analyzes Python code through 5 steps:

1. **Extract Functions** - Parses code and finds all function definitions
2. **Check Complexity** - Calculates cyclomatic complexity
3. **Detect Issues** - Finds code smells (long lines, missing docstrings, etc.)
4. **Suggest Improvements** - Generates actionable suggestions
5. **Check Quality** - Calculates quality score and loops if below threshold

### Workflow Flow

```
Start
  ↓
Extract Functions
  ↓
Check Complexity
  ↓
Detect Issues
  ↓
Suggest Improvements
  ↓
Check Quality Score
  ↓
Quality >= Threshold? ──No──→ Back to Check Complexity
  ↓ Yes
End
```

## Customizing the Workflow

### Change Quality Threshold

```python
initial_state = {
    "code": "...",
    "threshold": 8,  # Higher threshold = stricter quality requirements
    "max_iterations": 5  # More iterations allowed
}
```

### Test Different Code

```python
initial_state = {
    "code": """
def my_function(x, y):
    '''This function has a docstring'''
    return x + y
    """,
    "threshold": 7,
    "max_iterations": 3
}
```

## Troubleshooting

### Server won't start

**Error**: `Address already in use`

**Solution**: Kill the process using port 8000 or use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Import errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Test script fails

**Error**: `Connection refused`

**Solution**: Make sure the server is running in another terminal:
```bash
uvicorn app.main:app --reload
```

## Next Steps

- Read the [Architecture Documentation](ARCHITECTURE.md)
- Explore the [Full README](README.md)
- Check out the code in `app/` directory
- Try creating your own workflow
- Add custom tools to `app/tools.py`

## Common Use Cases

### 1. Simple Sequential Workflow

```json
{
  "nodes": {"a": {...}, "b": {...}, "c": {...}},
  "edges": {"a": "b", "b": "c"}
}
```

### 2. Conditional Branching

```json
{
  "nodes": {"check": {...}, "path_a": {...}, "path_b": {...}},
  "edges": {"check": "path_a"},
  "conditional_edges": {
    "check": {
      "condition": "value > 10",
      "true": "path_a",
      "false": "path_b"
    }
  }
}
```

### 3. Loop Until Condition

```json
{
  "nodes": {"process": {...}, "check": {...}},
  "edges": {"process": "check"},
  "conditional_edges": {
    "check": {
      "condition": "done == True",
      "true": "END",
      "false": "process"
    }
  }
}
```

## Support

For questions or issues:
- Check the [README](README.md)
- Review the [Architecture docs](ARCHITECTURE.md)
- Open an issue on GitHub

Happy workflow building! 🚀
