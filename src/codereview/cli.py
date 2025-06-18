"""Command-line interface for the AI code review agent."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

# Fix imports for both direct execution and package import
try:
    from .agent import CodeReviewAgent
except ImportError:
    # Add the src directory to the path for direct execution
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from codereview.agent import CodeReviewAgent

console = Console()


@click.group()
@click.version_option()
def main():
    """AI-powered code review agent using Google Gemini API."""
    pass


@main.command()
@click.option('--repo', '-r', 'repo_path', help='Path to git repository to analyze')
@click.option('--commits', '-c', help='Git commit range (e.g., HEAD~5..HEAD)')
@click.option('--output', '-o', help='Output file for results (JSON format)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(repo_path: Optional[str], commits: Optional[str], output: Optional[str], verbose: bool):
    """Analyze code changes in a repository."""
    if not repo_path:
        console.print("❌ Repository path is required. Use --repo or -r option.", style="bold red")
        sys.exit(1)
    
    try:
        agent = CodeReviewAgent()
        
        # Run the analysis
        console.print(f"🔍 Analyzing repository: {repo_path}", style="bold blue")
        if commits:
            console.print(f"📝 Commit range: {commits}", style="blue")
        
        # Run async function
        result = asyncio.run(agent.analyze_repository(repo_path, commits))
        
        if "error" in result:
            console.print(f"❌ Analysis failed: {result['error']}", style="bold red")
            sys.exit(1)
        
        # Display results
        _display_analysis_results(result, verbose)
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"💾 Results saved to: {output}", style="bold green")
    
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.option('--file', '-f', 'file_path', required=True, help='Path to file to analyze')
@click.option('--language', '-l', help='Programming language (auto-detected if not provided)')
@click.option('--output', '-o', help='Output file for results (JSON format)')
def analyze_file(file_path: str, language: Optional[str], output: Optional[str]):
    """Analyze a single file for code quality issues."""
    try:
        agent = CodeReviewAgent()
        
        console.print(f"🔍 Analyzing file: {file_path}", style="bold blue")
        
        # Run async function
        result = asyncio.run(agent.tools.analyze_file(file_path, language))
        
        if "error" in result:
            console.print(f"❌ Analysis failed: {result['error']}", style="bold red")
            sys.exit(1)
        
        # Display results
        _display_file_analysis_results(result)
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"💾 Results saved to: {output}", style="bold green")
    
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.option('--code', '-c', help='Code to analyze (or provide via stdin)')
@click.option('--language', '-l', required=True, help='Programming language')
@click.option('--task', '-t', help='Description of what the code is trying to accomplish')
@click.option('--output', '-o', help='Output file for results (JSON format)')
def suggest_algorithms(code: Optional[str], language: str, task: Optional[str], output: Optional[str]):
    """Suggest more efficient algorithms for given code."""
    try:
        # Get code from stdin if not provided
        if not code:
            console.print("📝 Enter your code (press Ctrl+D when done):", style="blue")
            code = sys.stdin.read().strip()
        
        if not code:
            console.print("❌ No code provided.", style="bold red")
            sys.exit(1)
        
        agent = CodeReviewAgent()
        
        console.print(f"🚀 Analyzing algorithms for {language} code...", style="bold blue")
        
        # Run async function
        result = asyncio.run(agent.tools.suggest_algorithms(code, language, task))
        
        if "error" in result:
            console.print(f"❌ Analysis failed: {result['error']}", style="bold red")
            sys.exit(1)
        
        # Display results
        _display_algorithm_suggestions(result)
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"💾 Results saved to: {output}", style="bold green")
    
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)


@main.command()
def interactive():
    """Start interactive mode for chat-based code review."""
    try:
        agent = CodeReviewAgent()
        asyncio.run(agent.run())
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.option('--port', '-p', default=8501, help='Port to run Streamlit on')
def web(port: int):
    """Launch the web interface using Streamlit."""
    try:
        try:
            from .web import run_streamlit
        except ImportError:
            # Add the src directory to the path for direct execution
            src_path = Path(__file__).parent.parent
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            from codereview.web import run_streamlit
        run_streamlit(port)
    except ImportError:
        console.print("❌ Streamlit not available. Install with: pip install streamlit", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)


def _display_analysis_results(result: dict, verbose: bool):
    """Display repository analysis results."""
    console.print("\n" + "="*60, style="bold blue")
    console.print("📊 ANALYSIS RESULTS", style="bold blue")
    console.print("="*60, style="bold blue")
    
    # Summary
    summary = result.get("summary", {})
    console.print(f"📁 Files analyzed: {summary.get('total_files', 0)}", style="green")
    console.print(f"⚠️  Issues found: {summary.get('total_issues', 0)}", style="yellow")
    console.print(f"💡 Suggestions: {summary.get('total_suggestions', 0)}", style="blue")
    
    # Files analyzed
    files = result.get("files_analyzed", [])
    if files:
        console.print("\n📋 FILES ANALYZED:", style="bold")
        for file_info in files:
            console.print(f"  • {file_info.get('file_path', 'Unknown')}", style="cyan")
            if verbose:
                issues = file_info.get("issues", [])
                if issues:
                    console.print(f"    Issues: {len(issues)}", style="yellow")
    
    # Algorithm suggestions
    suggestions = result.get("algorithm_suggestions", [])
    if suggestions:
        console.print("\n🚀 ALGORITHM SUGGESTIONS:", style="bold")
        for suggestion in suggestions:
            console.print(f"  • {suggestion}", style="green")


def _display_file_analysis_results(result: dict):
    """Display file analysis results."""
    console.print("\n" + "="*60, style="bold blue")
    console.print("📄 FILE ANALYSIS RESULTS", style="bold blue")
    console.print("="*60, style="bold blue")
    
    console.print(f"📁 File: {result.get('file_path', 'Unknown')}", style="cyan")
    console.print(f"🔤 Language: {result.get('language', 'Unknown')}", style="cyan")
    console.print(f"📏 Size: {result.get('size', 0)} characters, {result.get('lines', 0)} lines", style="cyan")
    
    # Issues
    issues = result.get("issues", [])
    if issues:
        console.print(f"\n⚠️  ISSUES FOUND ({len(issues)}):", style="bold yellow")
        for issue in issues:
            severity = issue.get("severity", "unknown").upper()
            severity_color = {
                "critical": "red",
                "high": "red",
                "medium": "yellow",
                "low": "blue"
            }.get(severity.lower(), "white")
            
            console.print(f"  [{severity}] {issue.get('description', 'No description')}", style=severity_color)
            if "line" in issue:
                console.print(f"    Line: {issue['line']}", style="dim")
    
    # Suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        console.print(f"\n💡 SUGGESTIONS ({len(suggestions)}):", style="bold blue")
        for suggestion in suggestions:
            console.print(f"  • {suggestion.get('description', 'No description')}", style="green")


def _display_algorithm_suggestions(result: dict):
    """Display algorithm analysis results."""
    console.print("\n" + "="*60, style="bold blue")
    console.print("🚀 ALGORITHM SUGGESTIONS", style="bold blue")
    console.print("="*60, style="bold blue")
    
    # Current complexity
    complexity = result.get("current_complexity", {})
    console.print(f"⏱️  Current Time Complexity: {complexity.get('time_complexity', 'Unknown')}", style="cyan")
    console.print(f"💾 Current Space Complexity: {complexity.get('space_complexity', 'Unknown')}", style="cyan")
    
    # Suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        console.print(f"\n💡 SUGGESTIONS ({len(suggestions)}):", style="bold blue")
        for suggestion in suggestions:
            priority = suggestion.get("priority", "medium").upper()
            priority_color = {
                "high": "red",
                "medium": "yellow",
                "low": "blue"
            }.get(priority.lower(), "white")
            
            console.print(f"  [{priority}] {suggestion.get('description', 'No description')}", style=priority_color)
            if "line" in suggestion:
                console.print(f"    Line: {suggestion['line']}", style="dim")
    
    # Improved algorithms
    improved = result.get("improved_algorithms", [])
    if improved:
        console.print(f"\n🔄 IMPROVED ALGORITHMS ({len(improved)}):", style="bold green")
        for algo in improved:
            console.print(f"  • {algo.get('pattern', 'Unknown pattern')}:", style="green")
            console.print(f"    Current: {algo.get('current', 'Unknown')}", style="dim")
            console.print(f"    Suggestion: {algo.get('suggestion', 'No suggestion')}", style="cyan")
            if "example" in algo:
                console.print(f"    Example: {algo['example']}", style="dim")


if __name__ == "__main__":
    main() 