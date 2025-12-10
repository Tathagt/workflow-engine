import requests
import time


def test_background_execution():
    
    
    print("=" * 60)
    print("Background Task Execution Test")
    print("=" * 60)
    

    print("\n1. Creating workflow graph...")
    
    graph_response = requests.post("http://localhost:8000/graph/create", json={
        "name": "code_review_background",
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
    
    graph_id = graph_response.json()["graph_id"]
    print(f"✓ Graph created: {graph_id}")
    
    print("\n2. Starting workflow in background...")
    
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
"""
    
    background_response = requests.post("http://localhost:8000/graph/run/background", json={
        "graph_id": graph_id,
        "initial_state": {
            "code": test_code,
            "threshold": 7,
            "max_iterations": 3
        }
    })
    
    result = background_response.json()
    run_id = result["run_id"]
    
    print(f"✓ Background task started!")
    print(f"  Run ID: {run_id}")
    print(f"  Status endpoint: {result['status_endpoint']}")
    
    
    print("\n3. Polling for task status...")
    print("-" * 60)
    
    max_polls = 20
    poll_count = 0
    
    while poll_count < max_polls:
        poll_count += 1
        
        
        task_status_response = requests.get(
            f"http://localhost:8000/graph/background/{run_id}/status"
        )
        task_status = task_status_response.json()
        
        
        state_response = requests.get(
            f"http://localhost:8000/graph/state/{run_id}"
        )
        state = state_response.json()
        
        task_status_value = task_status.get("task_status")
        workflow_status = state.get("status")
        current_node = state.get("current_node")
        
        print(f"[Poll {poll_count}] Task: {task_status_value} | Workflow: {workflow_status} | Node: {current_node}")
        
        
        if task_status_value == "completed" or workflow_status == "completed":
            print("\n✓ Workflow completed!")
            break
        
        if task_status_value == "failed":
            print(f"\n✗ Workflow failed: {task_status.get('error')}")
            break
        
        
        time.sleep(0.5)
    
    
    print("\n4. Fetching final results...")
    print("-" * 60)
    
    final_state_response = requests.get(
        f"http://localhost:8000/graph/state/{run_id}"
    )
    final_state = final_state_response.json()
    
    state_data = final_state.get("state", {})
    
    print(f"\nFinal Results:")
    print(f"  Status: {final_state.get('status')}")
    print(f"  Functions Found: {state_data.get('function_count', 0)}")
    print(f"  Average Complexity: {state_data.get('avg_complexity', 0):.2f}")
    print(f"  Issues Detected: {state_data.get('issue_count', 0)}")
    print(f"  Suggestions: {state_data.get('suggestion_count', 0)}")
    print(f"  Quality Score: {state_data.get('quality_score', 0):.2f}/10")
    print(f"  Iterations: {state_data.get('iteration', 0)}")
    
    
    print(f"\nExecution Log:")
    for log_entry in final_state.get("execution_log", []):
        node = log_entry.get("node")
        status = log_entry.get("status")
        print(f"  - {node}: {status}")
    
    print("\n" + "=" * 60)
    print("Background task test completed!")
    print("=" * 60)


def test_multiple_background_tasks():
    """Test running multiple workflows in parallel"""
    
    print("\n\n" + "=" * 60)
    print("Multiple Background Tasks Test")
    print("=" * 60)
    
    
    print("\n1. Creating workflow graph...")
    
    graph_response = requests.post("http://localhost:8000/graph/create", json={
        "name": "parallel_test",
        "nodes": {
            "extract": {"function": "extract_functions"},
            "analyze": {"function": "check_complexity"}
        },
        "edges": {
            "extract": "analyze"
        }
    })
    
    graph_id = graph_response.json()["graph_id"]
    print(f"✓ Graph created: {graph_id}")
    
    
    print("\n2. Starting 3 parallel workflows...")
    
    run_ids = []
    
    for i in range(3):
        code = f"""
def task_{i}_function():
    return {i}
"""
        
        response = requests.post("http://localhost:8000/graph/run/background", json={
            "graph_id": graph_id,
            "initial_state": {
                "code": code
            }
        })
        
        run_id = response.json()["run_id"]
        run_ids.append(run_id)
        print(f"  ✓ Task {i+1} started: {run_id[:8]}...")
    
    
    print("\n3. Waiting for all tasks to complete...")
    
    completed = [False] * 3
    max_wait = 10
    wait_count = 0
    
    while not all(completed) and wait_count < max_wait:
        wait_count += 1
        
        for i, run_id in enumerate(run_ids):
            if not completed[i]:
                response = requests.get(f"http://localhost:8000/graph/state/{run_id}")
                state = response.json()
                
                if state.get("status") == "completed":
                    completed[i] = True
                    print(f"  ✓ Task {i+1} completed")
        
        time.sleep(0.5)
    
    if all(completed):
        print("\n✓ All tasks completed successfully!")
    else:
        print(f"\n⚠️  {sum(completed)}/3 tasks completed")
    
    print("\n" + "=" * 60)
    print("Multiple background tasks test completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nBackground Task Execution Tests")
    print("Make sure the server is running: uvicorn app.main:app --reload\n")
    
    try:
        test_background_execution()
        test_multiple_background_tasks()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server.")
        print("Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {e}")
