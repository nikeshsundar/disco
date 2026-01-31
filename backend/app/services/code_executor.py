import subprocess
import tempfile
import os
import time
import platform
from typing import Dict, List, Any, Optional
import sys

# Only import resource on Unix-like systems
if platform.system() != 'Windows':
    import resource

# Timeout for code execution (seconds)
EXECUTION_TIMEOUT = 10
# Max memory (bytes) - 128MB
MAX_MEMORY = 128 * 1024 * 1024

def execute_python_code(code: str, test_cases: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed environment.
    Returns execution result with output, errors, and test results.
    """
    start_time = time.time()
    
    # Create temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = {
            "success": False,
            "output": "",
            "error": None,
            "test_results": [],
            "execution_time_ms": 0
        }
        
        # If no test cases, just run the code
        if not test_cases:
            try:
                proc = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=EXECUTION_TIMEOUT,
                    cwd=tempfile.gettempdir()
                )
                
                result["output"] = proc.stdout
                result["error"] = proc.stderr if proc.stderr else None
                result["success"] = proc.returncode == 0
                
            except subprocess.TimeoutExpired:
                result["error"] = "Execution timed out (limit: 10 seconds)"
            except Exception as e:
                result["error"] = str(e)
        else:
            # Run with test cases
            test_results = []
            all_passed = True
            
            for i, test_case in enumerate(test_cases):
                test_input = test_case.get("input", "")
                expected_output = str(test_case.get("expected_output", "")).strip()
                
                try:
                    proc = subprocess.run(
                        [sys.executable, temp_file],
                        input=test_input,
                        capture_output=True,
                        text=True,
                        timeout=EXECUTION_TIMEOUT,
                        cwd=tempfile.gettempdir()
                    )
                    
                    actual_output = proc.stdout.strip()
                    passed = actual_output == expected_output
                    
                    if not passed:
                        all_passed = False
                    
                    test_results.append({
                        "test_case": i + 1,
                        "input": test_input[:100],  # Truncate for display
                        "expected": expected_output[:100],
                        "actual": actual_output[:100],
                        "passed": passed,
                        "error": proc.stderr if proc.stderr else None
                    })
                    
                except subprocess.TimeoutExpired:
                    test_results.append({
                        "test_case": i + 1,
                        "passed": False,
                        "error": "Timeout"
                    })
                    all_passed = False
                except Exception as e:
                    test_results.append({
                        "test_case": i + 1,
                        "passed": False,
                        "error": str(e)
                    })
                    all_passed = False
            
            result["test_results"] = test_results
            result["success"] = all_passed
            result["output"] = f"Passed {sum(1 for t in test_results if t['passed'])}/{len(test_results)} test cases"
        
        result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
        return result
        
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass

def execute_javascript_code(code: str, test_cases: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Execute JavaScript code using Node.js"""
    start_time = time.time()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = {
            "success": False,
            "output": "",
            "error": None,
            "test_results": [],
            "execution_time_ms": 0
        }
        
        if not test_cases:
            try:
                proc = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=EXECUTION_TIMEOUT,
                    cwd=tempfile.gettempdir()
                )
                
                result["output"] = proc.stdout
                result["error"] = proc.stderr if proc.stderr else None
                result["success"] = proc.returncode == 0
                
            except subprocess.TimeoutExpired:
                result["error"] = "Execution timed out"
            except FileNotFoundError:
                result["error"] = "Node.js not installed"
            except Exception as e:
                result["error"] = str(e)
        else:
            # Similar test case handling as Python
            test_results = []
            all_passed = True
            
            for i, test_case in enumerate(test_cases):
                test_input = test_case.get("input", "")
                expected_output = str(test_case.get("expected_output", "")).strip()
                
                try:
                    proc = subprocess.run(
                        ["node", temp_file],
                        input=test_input,
                        capture_output=True,
                        text=True,
                        timeout=EXECUTION_TIMEOUT
                    )
                    
                    actual_output = proc.stdout.strip()
                    passed = actual_output == expected_output
                    
                    if not passed:
                        all_passed = False
                    
                    test_results.append({
                        "test_case": i + 1,
                        "passed": passed,
                        "expected": expected_output[:100],
                        "actual": actual_output[:100]
                    })
                    
                except Exception as e:
                    test_results.append({
                        "test_case": i + 1,
                        "passed": False,
                        "error": str(e)
                    })
                    all_passed = False
            
            result["test_results"] = test_results
            result["success"] = all_passed
        
        result["execution_time_ms"] = round((time.time() - start_time) * 1000, 2)
        return result
        
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def execute_code(code: str, language: str, test_cases: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Execute code in specified language"""
    language = language.lower()
    
    if language in ["python", "py", "python3"]:
        return execute_python_code(code, test_cases)
    elif language in ["javascript", "js", "node"]:
        return execute_javascript_code(code, test_cases)
    else:
        return {
            "success": False,
            "output": "",
            "error": f"Language '{language}' not supported. Supported: python, javascript",
            "test_results": [],
            "execution_time_ms": 0
        }

def validate_code_syntax(code: str, language: str) -> Dict[str, Any]:
    """Validate code syntax without executing"""
    if language.lower() in ["python", "py", "python3"]:
        try:
            compile(code, "<string>", "exec")
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"Line {e.lineno}: {e.msg}"}
    
    return {"valid": True, "error": None}  # Skip validation for other languages
