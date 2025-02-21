from typing import Any, Dict, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import ast
import re
import subprocess
from pathlib import Path

class CodeAnalysisInput(BaseModel):
    code: str = Field(..., description="The code to analyze")

class DependencyAnalyzerInput(BaseModel):
    project_path: str = Field(..., description="Path to the project root")

class SolutionValidatorInput(BaseModel):
    code: str = Field(..., description="The code solution to validate")

class CodeAnalysisTool(BaseTool):
    name: str = "code_analysis"
    description: str = """
    Analyzes Python code to identify potential issues, dependencies, and patterns.
    Input should be the actual code as a string.
    """
    args_schema: type[BaseModel] = CodeAnalysisInput

    def _run(self, code: str) -> Dict[str, Any]:
        try:
            # Parse the code and analyze structure
            tree = ast.parse(code)
            
            # Collect imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))
            
            # Analyze function calls and attributes
            function_calls = []
            attributes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        function_calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        attributes.append(f"{ast.unparse(node.func.value)}.{node.func.attr}")
            
            # Analyze class definitions
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                    classes.append({
                        'name': node.name,
                        'methods': methods
                    })
            
            # Analyze variables and their assignments
            variables = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append({
                                'name': target.id,
                                'value': ast.unparse(node.value)
                            })
            
            return {
                "imports": imports,
                "function_calls": function_calls,
                "attributes": attributes,
                "classes": classes,
                "variables": variables,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

class DependencyAnalyzer(BaseTool):
    name: str = "dependency_analyzer"
    description: str = """
    Analyzes project dependencies and version conflicts.
    Input should be the path to the project root.
    """
    args_schema: type[BaseModel] = DependencyAnalyzerInput

    def _run(self, project_path: str) -> Dict[str, Any]:
        try:
            # Run pip list to get installed packages
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True
            )
            
            # Check for common dependency files
            dep_files = []
            path = Path(project_path)
            
            common_dep_files = [
                "requirements.txt",
                "pyproject.toml",
                "setup.py",
                "Pipfile",
                "poetry.lock"
            ]
            
            for file in common_dep_files:
                if (path / file).exists():
                    dep_files.append(file)
            
            return {
                "installed_packages": result.stdout,
                "dependency_files": dep_files,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }

class SolutionValidator(BaseTool):
    name: str = "solution_validator"
    description: str = """
    Validates Python code solutions against best practices and common patterns.
    Input should be the code to validate as a string.
    """
    args_schema: type[BaseModel] = SolutionValidatorInput

    def _run(self, code: str) -> Dict[str, Any]:
        try:
            # Basic code quality checks
            quality_checks = {
                "has_docstring": '"""' in code or "'''" in code,
                "has_type_hints": bool(re.search(r":\s*[A-Za-z]+[\[\],\s]*", code)),
                "has_error_handling": "try:" in code and "except" in code,
                "follows_pep8": self._check_pep8(code)
            }
            
            # Check for common anti-patterns
            anti_patterns = {
                "bare_except": "except:" in code,
                "global_variables": bool(re.search(r"^[A-Z_]+\s*=", code, re.MULTILINE)),
                "mutable_defaults": bool(re.search(r"def.*\((.*=\[\].*|.*={}.*)\)", code))
            }
            
            # Parse and analyze the code structure
            tree = ast.parse(code)
            
            # Check for proper class structure
            class_issues = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in ast.walk(node) if isinstance(n, ast.FunctionDef)]
                    for method in methods:
                        args = [a.arg for a in method.args.args]
                        if len(args) > 0 and args[0] != 'self':
                            class_issues.append(f"Method '{method.name}' missing 'self' parameter")
            
            return {
                "quality_checks": quality_checks,
                "anti_patterns": anti_patterns,
                "class_issues": class_issues,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def _check_pep8(self, code: str) -> bool:
        # Basic PEP 8 checks
        checks = [
            code.count('\t') == 0,  # No tabs
            not any(line.rstrip().endswith(' ') for line in code.splitlines()),  # No trailing whitespace
            all(len(line) <= 79 for line in code.splitlines())  # Line length
        ]
        return all(checks)

# Create tool instances
code_analysis_tool = CodeAnalysisTool()
dependency_analyzer_tool = DependencyAnalyzer()
solution_validator_tool = SolutionValidator()
