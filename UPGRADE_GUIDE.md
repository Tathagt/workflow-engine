# Upgrade Guide - WebSocket & Background Tasks

This guide helps you upgrade your existing installation to include the new WebSocket streaming and background task features.

## 🔄 Quick Upgrade

If you already have the project installed:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install new dependencies
pip install websockets==12.0

# 4. Restart the server
uvicorn app.main:app --reload
```

## 📦 Fresh Installation

If you're installing from scratch:

```bash
# 1. Clone repository
git clone https://github.com/Tathagt/workflow-engine.git
cd workflow-engine

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Start server
uvicorn app.main:app --reload
```

## ✅ Verify Installation

### 1. Check Dependencies

```bash
pip list | grep websockets
```

You should see:
```
websockets    12.0
```

### 2. Check API Version

Visit: http://localhost:8000/

You should see:
```json
{
  "message": "Workflow Engine API",
  "version": "2.0.0",
  "features": [
    "Graph creation and execution",
    "WebSocket streaming",
    "Background task execution",
    "Conditional branching",
    "Looping support"
  ]
}
```

### 3. Check Health Endpoint

Visit: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "features": {
    "websocket_streaming": true,
    "background_tasks": true,
    "conditional_branching": true,
    "looping": true
  }
}
```

### 4. Test WebSocket

```bash
python examples/test_websocket.py
```

Expected output:
```
WebSocket Streaming Test
============================================================
1. Creating workflow graph...
✓ Graph created: abc-123

2. Connecting to WebSocket...
✓ WebSocket connected!
...
```

### 5. Test Background Tasks

```bash
python examples/test_background_tasks.py
```

Expected output:
```
Background Task Execution Test
============================================================
1. Creating workflow graph...
✓ Graph created: abc-123

2. Starting workflow in background...
✓ Background task started!
...
```

## 🆕 What's New

### New Endpoints

1. **WebSocket Streaming**
   ```
   ws://localhost:8000/ws/graph/run/{graph_id}
   ```

2. **Background Task Execution**
   ```
   POST /graph/run/background
   ```

3. **Background Task Status**
   ```
   GET /graph/background/{run_id}/status
   ```

### New Features

- ✅ Real-time workflow streaming via WebSocket
- ✅ Asynchronous background task execution
- ✅ Multiple parallel workflow support
- ✅ Enhanced status tracking
- ✅ Live progress updates

### Updated Files

- `app/main.py` - Added WebSocket and background endpoints
- `app/engine.py` - Added streaming and background support
- `requirements.txt` - Added websockets dependency
- `examples/test_websocket.py` - New WebSocket test
- `examples/test_background_tasks.py` - New background test

### New Documentation

- `WEBSOCKET_GUIDE.md` - Complete WebSocket & background tasks guide
- `FEATURES.md` - Comprehensive feature list
- `UPGRADE_GUIDE.md` - This file

## 🔧 Troubleshooting

### Issue: "Module 'websockets' not found"

**Solution:**
```bash
pip install websockets==12.0
```

### Issue: "WebSocket connection failed"

**Solution:**
1. Make sure server is running
2. Check if port 8000 is available
3. Verify firewall settings

### Issue: "Background task not found"

**Solution:**
- Background tasks are stored in memory
- They're cleared when server restarts
- Make sure you're using the correct run_id

### Issue: "Connection refused"

**Solution:**
```bash
# Make sure server is running
uvicorn app.main:app --reload

# Check if server is accessible
curl http://localhost:8000/health
```

## 📊 Compatibility

### Python Version
- **Minimum**: Python 3.8
- **Recommended**: Python 3.10+

### Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
websockets==12.0  # NEW!
```

### Operating Systems
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+)

## 🎯 Migration Guide

### From v1.0.0 to v2.0.0

**Breaking Changes:**
- None! All existing endpoints work the same way

**New Features:**
- WebSocket streaming (optional)
- Background tasks (optional)

**Code Changes Required:**
- None! Your existing code will continue to work

**Example Migration:**

**Before (v1.0.0):**
```python
# Synchronous execution only
response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {...}
})
```

**After (v2.0.0) - Still works!**
```python
# Same synchronous execution
response = requests.post("http://localhost:8000/graph/run", json={
    "graph_id": graph_id,
    "initial_state": {...}
})
```

**New Options (v2.0.0):**
```python
# Option 1: Background execution
response = requests.post("http://localhost:8000/graph/run/background", json={
    "graph_id": graph_id,
    "initial_state": {...}
})

# Option 2: WebSocket streaming
async with websockets.connect(f"ws://localhost:8000/ws/graph/run/{graph_id}") as ws:
    await ws.send(json.dumps({"initial_state": {...}}))
    # Receive real-time updates
```

## 📚 Next Steps

1. **Read the guides:**
   - [WEBSOCKET_GUIDE.md](WEBSOCKET_GUIDE.md) - WebSocket & background tasks
   - [QUICKSTART.md](QUICKSTART.md) - Getting started
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture details

2. **Try the examples:**
   ```bash
   python examples/test_websocket.py
   python examples/test_background_tasks.py
   ```

3. **Explore the API:**
   - Visit http://localhost:8000/docs
   - Try the new endpoints
   - Test WebSocket connections

4. **Build something:**
   - Create your own workflows
   - Add custom tools
   - Integrate with your apps

## 🆘 Getting Help

If you encounter issues:

1. **Check the documentation:**
   - README.md
   - WEBSOCKET_GUIDE.md
   - ARCHITECTURE.md

2. **Run the tests:**
   ```bash
   python examples/test_workflow.py
   python examples/test_websocket.py
   python examples/test_background_tasks.py
   ```

3. **Verify installation:**
   ```bash
   pip list
   curl http://localhost:8000/health
   ```

4. **Check server logs:**
   - Look at the terminal where uvicorn is running
   - Check for error messages

## ✅ Upgrade Checklist

- [ ] Pulled latest code from GitHub
- [ ] Activated virtual environment
- [ ] Installed websockets dependency
- [ ] Restarted server
- [ ] Verified API version (2.0.0)
- [ ] Checked health endpoint
- [ ] Tested WebSocket connection
- [ ] Tested background tasks
- [ ] Read WEBSOCKET_GUIDE.md
- [ ] Tried example scripts

---

**Congratulations! You're now running v2.0.0 with WebSocket streaming and background task support! 🎉**
