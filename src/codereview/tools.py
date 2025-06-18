"""Tools for code analysis and algorithm suggestions."""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import git
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class CodeAnalysisTools:
    """Tools for analyzing code and suggesting improvements."""

    def __init__(self):
        """Initialize the code analysis tools."""
        self.quality_dimensions = {
            "readability": "Code readability and clarity",
            "performance": "Performance and efficiency",
            "security": "Security vulnerabilities",
            "maintainability": "Code maintainability and structure",
            "best_practices": "Language-specific best practices",
            "algorithm_efficiency": "Algorithm complexity and efficiency"
        }

    async def analyze_code_changes(self, repository_path: str, commit_range: Optional[str] = None) -> Dict[str, Any]:
        """Analyze git changes for code quality issues.
        
        Args:
            repository_path: Path to the git repository
            commit_range: Git commit range to analyze
            
        Returns:
            Analysis results
        """
        try:
            repo = git.Repo(repository_path)
            
            # Determine commit range
            if commit_range:
                commits = list(repo.iter_commits(commit_range))
            else:
                # Default to last commit
                commits = [repo.head.commit]
            
            if not commits:
                return {"error": "No commits found in the specified range"}
            
            analysis_results = {
                "repository": repository_path,
                "commit_range": commit_range or "HEAD",
                "commits_analyzed": len(commits),
                "files_analyzed": [],
                "issues_found": [],
                "algorithm_suggestions": []
            }
            
            for commit in commits:
                console.print(f"📝 Analyzing commit: {commit.hexsha[:8]} - {commit.message.split()[0]}", style="blue")
                
                # Get diff for this commit
                if commit.parents:
                    diff = commit.diff(commit.parents[0])
                else:
                    # Initial commit
                    diff = commit.diff(git.NULL_TREE)
                
                for change in diff:
                    if change.a_path and change.a_path.endswith(('.py', '.js', '.java', '.cpp', '.c', '.go', '.rs')):
                        file_analysis = await self._analyze_file_change(change, commit)
                        if file_analysis:
                            analysis_results["files_analyzed"].append(file_analysis)
            
            # Generate summary
            analysis_results["summary"] = self._generate_analysis_summary(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            return {"error": f"Failed to analyze repository: {str(e)}"}

    async def suggest_algorithms(self, code: str, language: str, task_description: Optional[str] = None) -> Dict[str, Any]:
        """Suggest more efficient algorithms for a given code task.
        
        Args:
            code: The code to analyze
            language: Programming language of the code
            task_description: Description of what the code is trying to accomplish
            
        Returns:
            Algorithm suggestions and improvements
        """
        try:
            suggestions = {
                "original_code": code,
                "language": language,
                "task_description": task_description,
                "current_complexity": self._analyze_complexity(code, language),
                "suggestions": [],
                "improved_algorithms": []
            }
            
            # Analyze the code for algorithm improvements
            if language.lower() in ['python', 'py']:
                suggestions.update(await self._analyze_python_algorithms(code, task_description))
            elif language.lower() in ['javascript', 'js']:
                suggestions.update(await self._analyze_javascript_algorithms(code, task_description))
            elif language.lower() in ['java']:
                suggestions.update(await self._analyze_java_algorithms(code, task_description))
            else:
                suggestions["suggestions"].append({
                    "type": "general",
                    "description": "Consider analyzing time and space complexity",
                    "priority": "medium"
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting algorithms: {e}")
            return {"error": f"Failed to suggest algorithms: {str(e)}"}

    async def analyze_file(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a single file for code quality issues.
        
        Args:
            file_path: Path to the file to analyze
            language: Programming language (auto-detected if not provided)
            
        Returns:
            File analysis results
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Auto-detect language if not provided
            if not language:
                language = self._detect_language(path)
            
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            analysis = {
                "file_path": str(path),
                "language": language,
                "size": len(code),
                "lines": len(code.splitlines()),
                "issues": [],
                "suggestions": []
            }
            
            # Analyze based on language
            if language == "python":
                analysis.update(await self._analyze_python_file(code))
            elif language == "javascript":
                analysis.update(await self._analyze_javascript_file(code))
            else:
                analysis.update(await self._analyze_generic_file(code, language))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {"error": f"Failed to analyze file: {str(e)}"}

    async def _analyze_file_change(self, change: git.diff.Diff, commit: git.Commit) -> Optional[Dict[str, Any]]:
        """Analyze a single file change."""
        try:
            file_analysis = {
                "file_path": change.a_path or change.b_path,
                "change_type": change.change_type,
                "commit": commit.hexsha[:8],
                "commit_message": commit.message.split('\n')[0],
                "issues": [],
                "algorithm_suggestions": []
            }
            
            # Get the changed content
            if change.change_type == 'A':  # Added
                content = change.b_blob.data_stream.read().decode('utf-8')
                file_analysis["content"] = content
            elif change.change_type == 'M':  # Modified
                content = change.b_blob.data_stream.read().decode('utf-8')
                file_analysis["content"] = content
            elif change.change_type == 'D':  # Deleted
                content = change.a_blob.data_stream.read().decode('utf-8')
                file_analysis["content"] = content
            
            # Analyze the content
            language = self._detect_language(Path(file_analysis["file_path"]))
            if language == "python":
                file_analysis.update(await self._analyze_python_content(content))
            elif language == "javascript":
                file_analysis.update(await self._analyze_javascript_content(content))
            
            return file_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file change: {e}")
            return None

    async def _analyze_python_algorithms(self, code: str, task_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze Python code for algorithm improvements."""
        suggestions = []
        improved_algorithms = []
        
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Look for common inefficient patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check for nested loops
                    for child in ast.walk(node):
                        if isinstance(child, ast.For) and child != node:
                            suggestions.append({
                                "type": "nested_loops",
                                "description": "Nested loops detected - consider using itertools or list comprehensions",
                                "priority": "high",
                                "line": getattr(node, 'lineno', 'unknown')
                            })
                
                elif isinstance(node, ast.ListComp):
                    # Check for inefficient list comprehensions
                    if len(node.generators) > 1:
                        suggestions.append({
                            "type": "list_comprehension",
                            "description": "Complex list comprehension - consider using generator expressions",
                            "priority": "medium",
                            "line": getattr(node, 'lineno', 'unknown')
                        })
                
                elif isinstance(node, ast.Call):
                    # Check for inefficient function calls
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['sorted', 'list', 'tuple']:
                            suggestions.append({
                                "type": "function_call",
                                "description": f"Consider using {node.func.id}() more efficiently",
                                "priority": "low",
                                "line": getattr(node, 'lineno', 'unknown')
                            })
            
            # Suggest specific improvements based on patterns
            if "sort" in code.lower() or "sorted" in code:
                improved_algorithms.append({
                    "pattern": "sorting",
                    "current": "Using sorted() function",
                    "suggestion": "Consider using .sort() for in-place sorting or heapq for partial sorting",
                    "example": "data.sort()  # in-place\nheapq.nsmallest(5, data)  # partial sort"
                })
            
            if "for" in code and "in" in code and "range" in code:
                improved_algorithms.append({
                    "pattern": "iteration",
                    "current": "Using range() in loops",
                    "suggestion": "Consider using enumerate() for index access or direct iteration",
                    "example": "for i, item in enumerate(items):\n    print(f'{i}: {item}')"
                })
            
        except SyntaxError:
            suggestions.append({
                "type": "syntax_error",
                "description": "Code contains syntax errors",
                "priority": "critical"
            })
        
        return {
            "suggestions": suggestions,
            "improved_algorithms": improved_algorithms
        }

    async def _analyze_javascript_algorithms(self, code: str, task_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze JavaScript code for algorithm improvements."""
        suggestions = []
        improved_algorithms = []
        
        # Look for common inefficient patterns
        if "for (let i = 0; i < array.length; i++)" in code:
            suggestions.append({
                "type": "for_loop",
                "description": "Traditional for loop - consider using forEach, map, or for...of",
                "priority": "medium"
            })
        
        if "array.filter().map()" in code or "array.map().filter()" in code:
            suggestions.append({
                "type": "chaining",
                "description": "Multiple array operations - consider combining or using reduce",
                "priority": "medium"
            })
        
        if "JSON.parse(JSON.stringify(" in code:
            suggestions.append({
                "type": "deep_clone",
                "description": "Inefficient deep cloning - consider structuredClone() or lodash.cloneDeep",
                "priority": "medium"
            })
        
        return {
            "suggestions": suggestions,
            "improved_algorithms": improved_algorithms
        }

    async def _analyze_java_algorithms(self, code: str, task_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze Java code for algorithm improvements."""
        suggestions = []
        improved_algorithms = []
        
        # Look for common inefficient patterns
        if "for (int i = 0; i < list.size(); i++)" in code:
            suggestions.append({
                "type": "for_loop",
                "description": "Traditional for loop - consider using enhanced for loop or streams",
                "priority": "medium"
            })
        
        if "new ArrayList<>()" in code and "add(" in code:
            suggestions.append({
                "type": "list_creation",
                "description": "Consider using Arrays.asList() or List.of() for immutable lists",
                "priority": "low"
            })
        
        return {
            "suggestions": suggestions,
            "improved_algorithms": improved_algorithms
        }

    def _analyze_complexity(self, code: str, language: str) -> Dict[str, str]:
        """Analyze the time and space complexity of the code."""
        complexity = {
            "time_complexity": "O(n)",  # Default assumption
            "space_complexity": "O(1)",  # Default assumption
            "notes": []
        }
        
        # Simple heuristics for complexity analysis
        lines = code.split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['for', 'while', 'forEach']):
                if 'for' in line and 'in' in line and 'range' in line:
                    complexity["time_complexity"] = "O(n)"
                elif 'for' in line and 'for' in line:  # Nested loops
                    complexity["time_complexity"] = "O(n²)"
                    complexity["notes"].append("Nested loops detected")
        
        return complexity

    def _detect_language(self, file_path: Path) -> str:
        """Detect the programming language based on file extension."""
        extension = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby'
        }
        return language_map.get(extension, 'unknown')

    async def _analyze_python_file(self, code: str) -> Dict[str, Any]:
        """Analyze a Python file for quality issues."""
        issues = []
        suggestions = []
        
        try:
            tree = ast.parse(code)
            
            # Check for common issues
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 5:
                        issues.append({
                            "type": "too_many_parameters",
                            "description": f"Function '{node.name}' has too many parameters",
                            "severity": "medium",
                            "line": getattr(node, 'lineno', 'unknown')
                        })
                
                elif isinstance(node, ast.ClassDef):
                    if len(node.body) > 20:
                        issues.append({
                            "type": "large_class",
                            "description": f"Class '{node.name}' is too large",
                            "severity": "medium",
                            "line": getattr(node, 'lineno', 'unknown')
                        })
        
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "description": f"Syntax error: {str(e)}",
                "severity": "critical",
                "line": "unknown"
            })
        
        return {"issues": issues, "suggestions": suggestions}

    async def _analyze_javascript_file(self, code: str) -> Dict[str, Any]:
        """Analyze a JavaScript file for quality issues."""
        issues = []
        suggestions = []
        
        # Simple pattern matching for common issues
        if "var " in code:
            suggestions.append({
                "type": "var_usage",
                "description": "Consider using 'let' or 'const' instead of 'var'",
                "severity": "low"
            })
        
        if "console.log" in code:
            suggestions.append({
                "type": "console_log",
                "description": "Remove console.log statements before production",
                "severity": "low"
            })
        
        return {"issues": issues, "suggestions": suggestions}

    async def _analyze_generic_file(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze a generic file for quality issues."""
        issues = []
        suggestions = []
        
        # Generic analysis
        lines = code.split('\n')
        if len(lines) > 1000:
            issues.append({
                "type": "large_file",
                "description": "File is very large - consider splitting into smaller modules",
                "severity": "medium"
            })
        
        return {"issues": issues, "suggestions": suggestions}

    async def _analyze_python_content(self, content: str) -> Dict[str, Any]:
        """Analyze Python content for issues and suggestions."""
        return await self._analyze_python_file(content)

    async def _analyze_javascript_content(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript content for issues and suggestions."""
        return await self._analyze_javascript_file(content)

    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        total_issues = sum(len(file.get("issues", [])) for file in results.get("files_analyzed", []))
        total_suggestions = sum(len(file.get("suggestions", [])) for file in results.get("files_analyzed", []))
        
        return {
            "total_files": len(results.get("files_analyzed", [])),
            "total_issues": total_issues,
            "total_suggestions": total_suggestions,
            "severity_breakdown": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        } 