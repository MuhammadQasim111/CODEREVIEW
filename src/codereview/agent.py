"""AI-powered code review agent using Google Gemini API."""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import google.generativeai as genai
import aiofiles
import chardet
import fnmatch
from rich.console import Console
from rich.logging import RichHandler

# Fix imports for both direct execution and package import
try:
    from .tools import CodeAnalysisTools
    from .prompts import SYSTEM_PROMPT
except ImportError:
    src_path = Path(__file__).parent.parent
    if str(src_path) not in os.sys.path:
        os.sys.path.insert(0, str(src_path))
    from codereview.tools import CodeAnalysisTools
    from codereview.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)
console = Console()

class CodeReviewAgent:
    """
    AI agent for code review and analysis using Google Gemini API.
    Provides repository and file analysis with robust error handling, chunking, and async file reading.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the code review agent.
        Args:
            api_key (str, optional): GEMINI API key. If not provided, will try to load from environment.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI API key is required. Set GEMINI_API_KEY environment variable.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.tools = CodeAnalysisTools()
        self.conversation_history = []
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )

    async def send_message(self, message: str) -> str:
        """
        Send a message to the assistant and get a response.
        Args:
            message (str): The message to send to the assistant
        Returns:
            str: The assistant's response
        """
        self.conversation_history.append({"role": "user", "content": message})
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {message}"
        try:
            response = self.model.generate_content(full_prompt)
            assistant_response = response.text
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return f"Error: {str(e)}"

    async def analyze_repository(
        self,
        repo_path: str,
        file_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_files: int = 10,
        max_chars: int = 12000,
        chunk_size: int = 4000
    ) -> dict:
        """
        Analyze a repository for code quality issues using Gemini LLM.
        Args:
            repo_path (str): Path to the local repository.
            file_patterns (list[str], optional): Glob patterns to include (e.g., ['*.py', '*.js']).
            exclude_patterns (list[str], optional): Glob patterns to exclude (e.g., ['test_*', '*.min.js']).
            max_files (int): Max number of files to analyze.
            max_chars (int): Max total characters to send to LLM.
            chunk_size (int): Max characters per LLM chunk.
        Returns:
            dict: Analysis results and LLM feedback.
        """
        file_patterns = file_patterns or ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.go', '*.rs']
        exclude_patterns = exclude_patterns or ['test*', 'tests/*', '*.min.js', 'node_modules/*', 'build/*', 'dist/*']
        all_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                if any(fnmatch.fnmatch(file, pat) for pat in file_patterns) and not any(fnmatch.fnmatch(file_path, pat) for pat in exclude_patterns):
                    all_files.append(file_path)
        selected_files = all_files[:max_files]
        async def read_file_async(file_path):
            try:
                async with aiofiles.open(file_path, 'rb') as f:
                    raw = await f.read()
                encoding = chardet.detect(raw)['encoding'] or 'utf-8'
                text = raw.decode(encoding, errors='replace')
                return file_path, text, None
            except Exception as e:
                return file_path, None, str(e)
        tasks = [read_file_async(f) for f in selected_files]
        file_results = await asyncio.gather(*tasks)
        code_chunks = []
        errors = []
        total_chars = 0
        for file_path, code, err in file_results:
            if err:
                errors.append({'file': file_path, 'error': err})
                continue
            for i in range(0, len(code), chunk_size):
                chunk = code[i:i+chunk_size]
                if total_chars + len(chunk) > max_chars:
                    break
                code_chunks.append({'file': file_path, 'code': chunk})
                total_chars += len(chunk)
            if total_chars >= max_chars:
                break
        analyses = []
        for chunk in code_chunks:
            prompt = (
                f"You are an expert code reviewer. Analyze the following code for quality, maintainability, performance, and improvements. "
                f"Provide a summary of issues and suggestions.\n\n"
                f"File: {chunk['file']}\n\n"
                f"{chunk['code']}"
            )
            try:
                response = self.model.generate_content(prompt)
                analyses.append({
                    'file': chunk['file'],
                    'analysis': response.text
                })
            except Exception as e:
                analyses.append({
                    'file': chunk['file'],
                    'error': str(e)
                })
        return {
            'files_analyzed': [f for f, _, _ in file_results if _],
            'errors': errors,
            'analyses': analyses,
            'summary': {
                'total_files_found': len(all_files),
                'files_analyzed': len(selected_files),
                'chunks_analyzed': len(analyses)
            }
        }

    async def analyze_file_with_llm(self, file_path: str, language: Optional[str] = None) -> dict:
        """
        Analyze a single file for code quality issues using Gemini LLM.
        Args:
            file_path (str): Path to the file to analyze.
            language (str, optional): Programming language (for prompt context).
        Returns:
            dict: File analysis results and LLM feedback.
        """
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                raw = await f.read()
            encoding = chardet.detect(raw)['encoding'] or 'utf-8'
            code = raw.decode(encoding, errors='replace')
            prompt = (
                f"You are an expert code reviewer. Analyze the following {language or 'code'} file for code quality, maintainability, performance, and improvements. "
                f"Provide a summary of issues and suggestions.\n\n"
                f"File: {file_path}\n\n"
                f"{code}"
            )
            response = self.model.generate_content(prompt)
            analysis = response.text
            return {
                "file_path": file_path,
                "language": language,
                "size": len(code),
                "lines": len(code.splitlines()),
                "llm_analysis": analysis,
            }
        except Exception as e:
            return {"error": str(e)}

    async def analyze_code_with_tools(self, code: str, language: str, task_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze code using the built-in tools and then get AI feedback.
        
        Args:
            code: The code to analyze
            language: Programming language
            task_description: Description of the task
            
        Returns:
            Combined analysis results
        """
        # First, use the tools for technical analysis
        tool_results = await self.tools.suggest_algorithms(code, language, task_description)
        
        # Then, get AI feedback on the results
        ai_prompt = f"""
        I've analyzed this {language} code using technical tools. Here are the results:
        
        Code:
        ```{language}
        {code}
        ```
        
        Technical Analysis Results:
        {json.dumps(tool_results, indent=2)}
        
        Please provide additional insights, suggestions, and improvements based on these results.
        Focus on:
        1. Code quality improvements
        2. Additional algorithm optimizations
        3. Best practices recommendations
        4. Security considerations
        5. Performance enhancements
        """
        
        ai_feedback = await self.send_message(ai_prompt)
        
        return {
            "technical_analysis": tool_results,
            "ai_feedback": ai_feedback,
            "combined_results": {
                "code": code,
                "language": language,
                "task_description": task_description,
                "technical_findings": tool_results,
                "ai_insights": ai_feedback
            }
        }

    async def run(self):
        """Run the interactive code review agent."""
        try:
            console.print("\n🚀 Code Review Agent is ready!", style="bold green")
            console.print("Ask me to analyze code, suggest algorithms, or review changes.", style="blue")
            console.print("Type 'quit' to exit.\n", style="yellow")
            
            while True:
                try:
                    user_input = console.input("[bold cyan]You: [/bold cyan]")
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        console.print("👋 Goodbye!", style="bold green")
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    console.print("\n[bold yellow]🤖 Assistant:[/bold yellow]")
                    response = await self.send_message(user_input)
                    console.print(response, style="white")
                    console.print()
                    
                except KeyboardInterrupt:
                    console.print("\n👋 Goodbye!", style="bold green")
                    break
                except Exception as e:
                    console.print(f"❌ Error: {e}", style="bold red")
                    
        except Exception as e:
            console.print(f"❌ Failed to start agent: {e}", style="bold red")
            raise 