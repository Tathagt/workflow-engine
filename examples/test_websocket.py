"""
WebSocket streaming example - demonstrates real-time workflow execution
"""
import asyncio
import websockets
import json


async def test_websocket_streaming():
    """Test WebSocket streaming of workflow execution"""
    
    print("=" * 60)
    print("WebSocket Streaming Test")
    print("=" * 60)
    
    # First, create a graph
    import requests
    
    print("\n1. Creating workflow graph...")
    graph_response = requests.post("http://localhost:8000/graph/create", json={
        "name": "code_review_streaming",
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
    
    # Connect to WebSocket
    print("\n2. Connecting to WebSocket...")
    uri = f"ws://localhost:8000/ws/graph/run/{graph_id}"
    
    async with websockets.connect(uri) as websocket:
        print("✓ WebSocket connected!")
        
        # Send initial state
        print("\n3. Sending initial state...")
        initial_state = {
            "initial_state": {
                "code": """
def calculate_sum(a, b):
    if a > 0:
        if b > 0:
            return a + b
    return 0

def process_list(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
""",
                "threshold": 7,
                "max_iterations": 3
            }
        }
        
        await websocket.send(json.dumps(initial_state))
        
        # Receive and display streaming events
        print("\n4. Receiving real-time updates...\n")
        print("-" * 60)
        
        event_count = 0
        
        while True:
            try:
                message = await websocket.recv()
                event = json.loads(message)
                event_count += 1
                
                event_type = event.get("type")
                
                if event_type == "connected":
                    print(f"[{event_count}] 🔗 {event['message']}")
                
                elif event_type == "status":
                    status = event.get("status")
                    if status == "started":
                        print(f"[{event_count}] ▶️  Workflow started")
                    elif status == "completed":
                        print(f"[{event_count}] ✅ Workflow completed")
                
                elif event_type == "node_start":
                    node = event.get("node")
                    iteration = event.get("iteration")
                    print(f"[{event_count}] 🔵 Node '{node}' started (iteration {iteration})")
                
                elif event_type == "node_complete":
                    node = event.get("node")
                    state_update = event.get("state_update", {})
                    print(f"[{event_count}] ✓  Node '{node}' completed")
                    
                    # Show interesting state updates
                    if "function_count" in state_update:
                        print(f"       → Functions found: {state_update['function_count']}")
                    if "complexity" in state_update:
                        print(f"       → Complexity: {state_update['complexity']}")
                    if "issue_count" in state_update:
                        print(f"       → Issues detected: {state_update['issue_count']}")
                    if "quality_score" in state_update:
                        print(f"       → Quality score: {state_update['quality_score']:.2f}/10")
                
                elif event_type == "transition":
                    from_node = event.get("from")
                    to_node = event.get("to")
                    print(f"[{event_count}] ➡️  Transition: {from_node} → {to_node}")
                
                elif event_type == "system":
                    message = event.get("message")
                    print(f"[{event_count}] ⚠️  System: {message}")
                
                elif event_type == "complete":
                    print(f"\n[{event_count}] 🎉 Final Results:")
                    print("-" * 60)
                    final_state = event.get("final_state", {})
                    print(f"  Run ID: {event.get('run_id')}")
                    print(f"  Functions: {final_state.get('function_count', 0)}")
                    print(f"  Issues: {final_state.get('issue_count', 0)}")
                    print(f"  Quality Score: {final_state.get('quality_score', 0):.2f}/10")
                    print(f"  Iterations: {final_state.get('iteration', 0)}")
                    break
                
                elif event_type == "error":
                    print(f"[{event_count}] ❌ Error: {event.get('error')}")
                    break
            
            except websockets.exceptions.ConnectionClosed:
                print("\n✓ WebSocket connection closed")
                break
        
        print("-" * 60)
        print(f"\nTotal events received: {event_count}")
    
    print("\n" + "=" * 60)
    print("WebSocket test completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nWebSocket Streaming Test")
    print("Make sure the server is running: uvicorn app.main:app --reload\n")
    
    try:
        asyncio.run(test_websocket_streaming())
    except ConnectionRefusedError:
        print("\n✗ Error: Could not connect to the server.")
        print("Please make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {e}")
