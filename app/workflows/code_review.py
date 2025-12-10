


CODE_REVIEW_GRAPH = {
    "name": "code_review_workflow",
    "nodes": {
        "extract": {
            "function": "extract_functions",
            "params": {}
        },
        "analyze": {
            "function": "check_complexity",
            "params": {}
        },
        "detect": {
            "function": "detect_issues",
            "params": {}
        },
        "suggest": {
            "function": "suggest_improvements",
            "params": {}
        },
        "check_quality": {
            "function": "check_quality_score",
            "params": {}
        }
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


EXAMPLE_CODE = """
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

EXAMPLE_INITIAL_STATE = {
    "code": EXAMPLE_CODE,
    "threshold": 7,
    "max_iterations": 3
}


def get_code_review_workflow():
    """Get the code review workflow definition"""
    return CODE_REVIEW_GRAPH


def get_example_state():
    """Get example initial state for testing"""
    return EXAMPLE_INITIAL_STATE
