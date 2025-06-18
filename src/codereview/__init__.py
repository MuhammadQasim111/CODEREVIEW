"""AI-powered code review agent using OpenAI Agents SDK."""

from .agent import CodeReviewAgent

def main() -> None:
    """Main entry point for the code review agent."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Launch web interface
        from .web import run_streamlit
        run_streamlit()
    else:
        # Launch CLI interface
        from .cli import main as cli_main
        cli_main()

__all__ = ["CodeReviewAgent", "main"]
