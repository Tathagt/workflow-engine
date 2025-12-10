
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
from app.models import (
    GraphDefinition,
    GraphCreateResponse,
    RunRequest,
    RunResponse,
    StateResponse,
    ExecutionStatus
)
from app.engine import workflow_engine

app = FastAPI(
    title="Workflow Engine API",
    description="A minimal workflow engine with support for nodes, edges, branching, looping, WebSocket streaming, and background tasks",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    
    return {
        "message": "Workflow Engine API",
        "version": "2.0.0",
        "features": [
            "Graph creation and execution",
            "WebSocket streaming",
            "Background task execution",
            "Conditional branching",
            "Looping support"
        ],
        "docs": "/docs"
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(graph_def: GraphDefinition):
    
    try:
        graph_id = workflow_engine.create_graph(graph_def)
        return GraphCreateResponse(
            graph_id=graph_id,
            message="Graph created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=RunResponse)
async def run_graph(run_request: RunRequest):
   
    try:
        result = await workflow_engine.run_graph(
            run_request.graph_id,
            run_request.initial_state
        )
        
        return RunResponse(
            run_id=result["run_id"],
            final_state=result["state"],
            execution_log=result["execution_log"],
            status=result["status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/graph/run/background")
async def run_graph_background(run_request: RunRequest):
    
    try:
        run_id = await workflow_engine.run_graph_background(
            run_request.graph_id,
            run_request.initial_state
        )
        
        return {
            "run_id": run_id,
            "message": "Workflow started in background",
            "status_endpoint": f"/graph/state/{run_id}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=StateResponse)
async def get_workflow_state(run_id: str):
    
    run_state = workflow_engine.get_run_state(run_id)
    
    if not run_state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    
    return StateResponse(
        run_id=run_id,
        status=run_state["status"],
        current_node=run_state.get("current_node"),
        state=run_state["state"],
        execution_log=run_state["execution_log"]
    )


@app.get("/graph/background/{run_id}/status")
async def get_background_task_status(run_id: str):
    
    task_status = workflow_engine.get_background_task_status(run_id)
    run_state = workflow_engine.get_run_state(run_id)
    
    if task_status["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Background task {run_id} not found")
    
    response = {
        "run_id": run_id,
        "task_status": task_status["status"]
    }
    
    if run_state:
        response["workflow_status"] = run_state.get("status")
        response["current_node"] = run_state.get("current_node")
    
    if "error" in task_status:
        response["error"] = task_status["error"]
    
    return response


@app.websocket("/ws/graph/run/{graph_id}")
async def websocket_run_graph(websocket: WebSocket, graph_id: str):
    
    await websocket.accept()
    
    try:
        # Receive initial state from client
        data = await websocket.receive_text()
        request_data = json.loads(data)
        initial_state = request_data.get("initial_state", {})
        
        # Send acknowledgment
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "graph_id": graph_id
        })
        
        # Define streaming callback
        async def stream_callback(event: dict):
            """Send events to WebSocket client"""
            await websocket.send_json(event)
        
        # Execute workflow with streaming
        try:
            result = await workflow_engine.run_graph(
                graph_id,
                initial_state,
                stream_callback=stream_callback
            )
            
            # Send final result
            await websocket.send_json({
                "type": "complete",
                "run_id": result["run_id"],
                "final_state": result["state"],
                "execution_log": [
                    {
                        "node": log.node,
                        "status": log.status,
                        "timestamp": log.timestamp.isoformat(),
                        "details": log.details
                    }
                    for log in result["execution_log"]
                ]
            })
            
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "error": str(e),
                "message": "Workflow execution failed"
            })
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for graph {graph_id}")
    except json.JSONDecodeError:
        await websocket.send_json({
            "type": "error",
            "error": "Invalid JSON format",
            "message": "Please send valid JSON with 'initial_state' field"
        })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "message": "An unexpected error occurred"
        })
    finally:
        await websocket.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "features": {
            "websocket_streaming": True,
            "background_tasks": True,
            "conditional_branching": True,
            "looping": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
