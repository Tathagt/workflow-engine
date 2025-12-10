## WebSocket Streaming & Background Tasks Guide

This guide covers the advanced features: **WebSocket streaming** and **background task execution**.

## 🌐 WebSocket Streaming

WebSocket streaming provides **real-time updates** during workflow execution. Perfect for long-running workflows where you want to see progress as it happens.

### Features

- ✅ Real-time node execution updates
- ✅ Live state changes
- ✅ Progress tracking
- ✅ Error notifications
- ✅ Completion events

### WebSocket Endpoint

```
ws://localhost:8000/ws/graph/run/{graph_id}
```

### Message Flow

**1. Client Connects**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/graph/run/YOUR_GRAPH_ID');
```

**2. Client Sends Initial State**
```json
{
  "initial_state": {
    "code": "def hello(): pass",
    "threshold": 7,
    "max_iterations": 3
  }
}
```

**3. Server Streams Events**

The server sends various event types:

#### Connection Event
```json
{
  "type": "connected",
  "message": "WebSocket connection established",
  "graph_id": "abc-123"
}
```

#### Status Events
```json
{
  "type": "status",
  "run_id": "xyz-789",
  "status": "started",
  "timestamp": "2025-12-10T12:00:00"
}
```

#### Node Start Event
```json
{
  "type": "node_start",
  "node": "extract_functions",
  "iteration": 1,
  "timestamp": "2025-12-10T12:00:01"
}
```

#### Node Complete Event
```json
{
  "type": "node_complete",
  "node": "extract_functions",
  "state_update": {
    "function_count": 2,
    "functions": [...]
  },
  "timestamp": "2025-12-10T12:00:02"
}
```

#### Transition Event
```json
{
  "type": "transition",
  "from": "extract",
  "to": "analyze",
  "timestamp": "2025-12-10T12:00:02"
}
```

#### System Event
```json
{
  "type": "system",
  "message": "Max iterations reached",
  "timestamp": "2025-12-10T12:00:10"
}
```

#### Complete Event
```json
{
  "type": "complete",
  "run_id": "xyz-789",
  "final_state": {...},
  "execution_log": [...]
}
```

#### Error Event
```json
{
  "type": "error",
  "error": "Error message",
  "message": "Workflow execution failed"
}
```

### Python Example

```python
import asyncio
import websockets
import json

async def stream_workflow():
    uri = "ws://localhost:8000/ws/graph/run/YOUR_GRAPH_ID"
    
    async with websockets.connect(uri) as websocket:
        # Send initial state
        await websocket.send(json.dumps({
            "initial_state": {
                "code": "def test(): pass",
                "threshold": 7
            }
        }))
        
        # Receive events
        while True:
            message = await websocket.recv()
            event = json.loads(message)
            
            print(f"Event: {event['type']}")
            
            if event['type'] == 'complete':
                print("Workflow completed!")
                break

asyncio.run(stream_workflow())
```

### JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/graph/run/YOUR_GRAPH_ID');

ws.onopen = () => {
  // Send initial state
  ws.send(JSON.stringify({
    initial_state: {
      code: "def test(): pass",
      threshold: 7
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'connected':
      console.log('Connected to workflow engine');
      break;
    case 'node_start':
      console.log(`Node ${data.node} started`);
      break;
    case 'node_complete':
      console.log(`Node ${data.node} completed`);
      break;
    case 'complete':
      console.log('Workflow completed!', data.final_state);
      ws.close();
      break;
    case 'error':
      console.error('Error:', data.error);
      break;
  }
};
```

### Testing WebSocket

Run the included test script:

```bash
pip install websockets
python examples/test_websocket.py
```

Expected output:
```
[1] 🔗 WebSocket connection established
[2] ▶️  Workflow started
[3] 🔵 Node 'extract' started (iteration 1)
[4] ✓  Node 'extract' completed
       → Functions found: 2
[5] ➡️  Transition: extract → analyze
[6] 🔵 Node 'analyze' started (iteration 1)
...
```

## 🔄 Background Task Execution

Background tasks allow workflows to run **asynchronously** without blocking the API response. Perfect for long-running workflows.

### Features

- ✅ Non-blocking execution
- ✅ Multiple parallel workflows
- ✅ Status polling
- ✅ Progress tracking
- ✅ Error handling

### Endpoints

#### Start Background Task
```
POST /graph/run/background
```

**Request:**
```json
{
  "graph_id": "abc-123",
  "initial_state": {
    "code": "def test(): pass",
    "threshold": 7
  }
}
```

**Response:**
```json
{
  "run_id": "xyz-789",
  "message": "Workflow started in background",
  "status_endpoint": "/graph/state/xyz-789"
}
```

#### Check Background Task Status
```
GET /graph/background/{run_id}/status
```

**Response:**
```json
{
  "run_id": "xyz-789",
  "task_status": "running",
  "workflow_status": "running",
  "current_node": "analyze"
}
```

Possible `task_status` values:
- `running` - Task is executing
- `completed` - Task finished successfully
- `failed` - Task encountered an error
- `not_found` - Task doesn't exist

#### Get Workflow State
```
GET /graph/state/{run_id}
```

**Response:**
```json
{
  "run_id": "xyz-789",
  "status": "completed",
  "current_node": "END",
  "state": {...},
  "execution_log": [...]
}
```

### Python Example

```python
import requests
import time

# Start background task
response = requests.post("http://localhost:8000/graph/run/background", json={
    "graph_id": "abc-123",
    "initial_state": {
        "code": "def test(): pass",
        "threshold": 7
    }
})

run_id = response.json()["run_id"]
print(f"Task started: {run_id}")

# Poll for completion
while True:
    status = requests.get(f"http://localhost:8000/graph/background/{run_id}/status")
    task_status = status.json()["task_status"]
    
    print(f"Status: {task_status}")
    
    if task_status in ["completed", "failed"]:
        break
    
    time.sleep(1)

# Get final results
result = requests.get(f"http://localhost:8000/graph/state/{run_id}")
print("Final state:", result.json())
```

### Testing Background Tasks

Run the included test script:

```bash
python examples/test_background_tasks.py
```

Expected output:
```
1. Creating workflow graph...
✓ Graph created: abc-123

2. Starting workflow in background...
✓ Background task started!
  Run ID: xyz-789

3. Polling for task status...
[Poll 1] Task: running | Workflow: running | Node: extract
[Poll 2] Task: running | Workflow: running | Node: analyze
[Poll 3] Task: completed | Workflow: completed | Node: END

✓ Workflow completed!

4. Fetching final results...
  Functions Found: 3
  Quality Score: 8.5/10
```

## 🎯 Use Cases

### WebSocket Streaming
- **Real-time dashboards** - Show live workflow progress
- **Interactive UIs** - Update UI as workflow executes
- **Debugging** - See exactly what's happening
- **Long workflows** - Track progress of lengthy operations

### Background Tasks
- **Batch processing** - Process multiple workflows in parallel
- **Scheduled jobs** - Run workflows on a schedule
- **API responsiveness** - Don't block API responses
- **Resource management** - Control concurrent executions

## 🔧 Advanced Usage

### Running Multiple Workflows in Parallel

```python
import requests

# Start 5 workflows in parallel
run_ids = []

for i in range(5):
    response = requests.post("http://localhost:8000/graph/run/background", json={
        "graph_id": "abc-123",
        "initial_state": {"code": f"def task_{i}(): pass"}
    })
    run_ids.append(response.json()["run_id"])

# Wait for all to complete
completed = []
while len(completed) < 5:
    for run_id in run_ids:
        if run_id not in completed:
            status = requests.get(f"http://localhost:8000/graph/background/{run_id}/status")
            if status.json()["task_status"] == "completed":
                completed.append(run_id)
                print(f"Task {run_id} completed!")
```

### Combining WebSocket + Background Tasks

```python
# Start background task
response = requests.post("http://localhost:8000/graph/run/background", ...)
run_id = response.json()["run_id"]

# Monitor via polling
while True:
    status = requests.get(f"http://localhost:8000/graph/state/{run_id}")
    print(f"Current node: {status.json()['current_node']}")
    
    if status.json()["status"] == "completed":
        break
    
    time.sleep(1)
```

## 📊 Performance Considerations

### WebSocket
- **Connection limit**: Depends on server resources
- **Message size**: Keep state updates small
- **Reconnection**: Implement reconnection logic in clients

### Background Tasks
- **Concurrency**: Limited by asyncio event loop
- **Memory**: Each task stores state in memory
- **Cleanup**: Tasks are kept in memory until server restart

## 🐛 Troubleshooting

### WebSocket Connection Fails
```
Error: Connection refused
```
**Solution**: Make sure server is running and WebSocket support is enabled

### Background Task Not Found
```
{"status": "not_found"}
```
**Solution**: Task may have been cleaned up or run_id is incorrect

### WebSocket Disconnects
```
ConnectionClosed
```
**Solution**: Implement reconnection logic with exponential backoff

## 📚 Additional Resources

- [FastAPI WebSockets Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

## ✅ Summary

| Feature | Endpoint | Use Case |
|---------|----------|----------|
| **Synchronous Execution** | `POST /graph/run` | Quick workflows, immediate results |
| **WebSocket Streaming** | `ws://...` | Real-time updates, live dashboards |
| **Background Tasks** | `POST /graph/run/background` | Long workflows, parallel execution |

Choose the right approach based on your needs! 🚀
