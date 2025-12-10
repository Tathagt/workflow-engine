
from typing import Dict, Any, Callable
import re
import ast


class ToolRegistry:
    
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable) -> None:
        """Register a tool function"""
        self._tools[name] = func
    
    def get(self, name: str) -> Callable:
        """Get a tool function by name"""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def list_tools(self) -> list:
        """List all registered tools"""
        return list(self._tools.keys())



tool_registry = ToolRegistry()




def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract function definitions from code"""
    code = state.get("code", "")
    functions = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "body_lines": len(node.body)
                })
    except SyntaxError:
        
        pattern = r'def\s+(\w+)\s*\([^)]*\):'
        matches = re.finditer(pattern, code)
        for match in matches:
            functions.append({
                "name": match.group(1),
                "line_start": code[:match.start()].count('\n') + 1
            })
    
    state["functions"] = functions
    state["function_count"] = len(functions)
    return state


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze code complexity"""
    code = state.get("code", "")
    functions = state.get("functions", [])
    
    complexity_scores = []
    
    for func in functions:
        
        func_name = func.get("name", "")
        
       
        if_count = code.count(f"if ") + code.count(f"elif ")
        for_count = code.count(f"for ")
        while_count = code.count(f"while ")
        try_count = code.count(f"try:")
        
        
        complexity = 1 + if_count + for_count + while_count + try_count
        
        complexity_scores.append({
            "function": func_name,
            "complexity": complexity
        })
    
    state["complexity_scores"] = complexity_scores
    state["avg_complexity"] = sum(s["complexity"] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0
    
    return state


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detect code smells and basic issues"""
    code = state.get("code", "")
    issues = []
    
   
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        
        if len(line) > 100:
            issues.append({
                "line": i,
                "type": "long_line",
                "message": f"Line exceeds 100 characters ({len(line)} chars)"
            })
        
        
        if ';' in line and not line.strip().startswith('#'):
            issues.append({
                "line": i,
                "type": "multiple_statements",
                "message": "Multiple statements on one line"
            })
        
        
        if line.strip().startswith('def ') and i < len(lines):
            next_line = lines[i].strip() if i < len(lines) else ""
            if not next_line.startswith('"""') and not next_line.startswith("'''"):
                func_name = line.split('def ')[1].split('(')[0]
                issues.append({
                    "line": i,
                    "type": "missing_docstring",
                    "message": f"Function '{func_name}' missing docstring"
                })
    
   
    complexity_scores = state.get("complexity_scores", [])
    for score in complexity_scores:
        if score["complexity"] > 10:
            issues.append({
                "type": "high_complexity",
                "function": score["function"],
                "message": f"High complexity: {score['complexity']}"
            })
    
    state["issues"] = issues
    state["issue_count"] = len(issues)
    
    return state


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate improvement suggestions"""
    issues = state.get("issues", [])
    suggestions = []
    
    issue_types = {}
    for issue in issues:
        issue_type = issue.get("type", "unknown")
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
    
    
    if issue_types.get("long_line", 0) > 0:
        suggestions.append({
            "category": "formatting",
            "suggestion": "Break long lines into multiple lines for better readability",
            "priority": "medium"
        })
    
    if issue_types.get("missing_docstring", 0) > 0:
        suggestions.append({
            "category": "documentation",
            "suggestion": "Add docstrings to all functions explaining their purpose",
            "priority": "high"
        })
    
    if issue_types.get("high_complexity", 0) > 0:
        suggestions.append({
            "category": "refactoring",
            "suggestion": "Refactor complex functions into smaller, more manageable pieces",
            "priority": "high"
        })
    
    if issue_types.get("multiple_statements", 0) > 0:
        suggestions.append({
            "category": "formatting",
            "suggestion": "Use separate lines for each statement",
            "priority": "low"
        })
    
    state["suggestions"] = suggestions
    state["suggestion_count"] = len(suggestions)
    
    return state


def check_quality_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall quality score"""
    issue_count = state.get("issue_count", 0)
    function_count = state.get("function_count", 1)
    avg_complexity = state.get("avg_complexity", 0)
    
    
    quality_score = 10.0
    
    
    quality_score -= min(issue_count * 0.5, 5)
    
    
    if avg_complexity > 10:
        quality_score -= 2
    elif avg_complexity > 5:
        quality_score -= 1
    
    
    quality_score = max(0, min(10, quality_score))
    
    state["quality_score"] = quality_score
    
    
    iteration = state.get("iteration", 0) + 1
    state["iteration"] = iteration
    
    return state



tool_registry.register("extract_functions", extract_functions)
tool_registry.register("check_complexity", check_complexity)
tool_registry.register("detect_issues", detect_issues)
tool_registry.register("suggest_improvements", suggest_improvements)
tool_registry.register("check_quality_score", check_quality_score)
