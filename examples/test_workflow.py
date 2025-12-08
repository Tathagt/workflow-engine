"""
Test script to demonstrate the workflow engine
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_code_review_workflow():
    """Test the code review workflow"""
    
    print("=" * 60)
    print("Testing Code Review Workflow")
    print("=" * 60)
    
    # Step 1: Create the graph
    print("\n1. Creating workflow graph...")
    
    graph_definition = {
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
    
    response = requests.post(f"{BASE_URL}/graph/create", json=graph_definition)
    
    if response.status_code == 200:
        result = response.json()
        graph_id = result["graph_id"]
        print(f"✓ Graph created successfully!")
        print(f"  Graph ID: {graph_id}")
    else:
        print(f"✗ Failed to create graph: {response.text}")
        return
    
    # Step 2: Run the workflow
    print("\n2. Running workflow...")
    
    test_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total

def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result

def complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0
"""
    
    run_request = {
        "graph_id": graph_id,
        "initial_state": {
            "code": test_code,
            "threshold": 7,
            "max_iterations": 3
        }
    }
    
    response = requests.post(f"{BASE_URL}/graph/run", json=run_request)
    
    if response.status_code == 200:
        result = response.json()
        run_id = result["run_id"]
        print(f"✓ Workflow executed successfully!")
        print(f"  Run ID: {run_id}")
        
        # Display results
        print("\n3. Workflow Results:")
        print("-" * 60)
        
        final_state = result["final_state"]
        
        print(f"\n  Functions Found: {final_state.get('function_count', 0)}")
        print(f"  Issues Detected: {final_state.get('issue_count', 0)}")
        print(f"  Suggestions: {final_state.get('suggestion_count', 0)}")
        print(f"  Quality Score: {final_state.get('quality_score', 0):.2f}/10")
        print(f"  Iterations: {final_state.get('iteration', 0)}")
        
        # Display issues
        if final_state.get('issues'):
            print("\n  Issues Found:")
            for issue in final_state['issues'][:5]:  # Show first 5
                print(f"    - {issue.get('type')}: {issue.get('message')}")
        
        # Display suggestions
        if final_state.get('suggestions'):
            print("\n  Suggestions:")
            for suggestion in final_state['suggestions']:
                print(f"    - [{suggestion.get('priority')}] {suggestion.get('suggestion')}")
        
        # Display execution log
        print("\n4. Execution Log:")
        print("-" * 60)
        for log_entry in result["execution_log"]:
            node = log_entry.get('node')
            status = log_entry.get('status')
            print(f"  {node}: {status}")
        
        # Step 3: Query the state
        print("\n5. Querying workflow state...")
        response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
        
        if response.status_code == 200:
            state_result = response.json()
            print(f"✓ State retrieved successfully!")
            print(f"  Status: {state_result['status']}")
            print(f"  Current Node: {state_result.get('current_node', 'END')}")
        
    else:
        print(f"✗ Failed to run workflow: {response.text}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


def test_health_check():
    """Test the health check endpoint"""
    print("\nTesting health check...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✓ API is healthy!")
    else:
        print("✗ API health check failed")


if __name__ == "__main__":
    print("\nWorkflow Engine Test Suite")
    print("Make sure the server is running: uvicorn app.main:app --reload\n")
    
    time.sleep(1)
    
    try:
        test_health_check()
        test_code_review_workflow()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the API server.")
        print("Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {e}")
