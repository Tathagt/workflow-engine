"""
FastAPI application for workflow engine
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    description="A minimal workflow/graph engine with support for nodes, edges, branching, and looping",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Workflow Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(graph_def: GraphDefinition):
    """
    Create a new workflow graph
    
    Args:
        graph_def: Graph definition with nodes, edges, and conditional edges
    
    Returns:
        GraphCreateResponse with graph_id
    """
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
    """
    Execute a workflow graph
    
    Args:
        run_request: Contains graph_id and initial_state
    
    Returns:
        RunResponse with run_id, final_state, and execution_log
    """
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


@app.get("/graph/state/{run_id}", response_model=StateResponse)
async def get_workflow_state(run_id: str):
    """
    Get the current state of a workflow run
    
    Args:
        run_id: The ID of the workflow run
    
    Returns:
        StateResponse with current state and execution log
    """
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
