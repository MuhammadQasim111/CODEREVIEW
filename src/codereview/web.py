"""Streamlit web interface for the AI code review agent."""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Optional
import os
import git
import re
import shutil
import stat

import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from dotenv import load_dotenv
load_dotenv()
print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
try:
    from .agent import CodeReviewAgent
except ImportError:
    from codereview.agent import CodeReviewAgent


def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def run_streamlit(port: int = 8501):
    """Run the Streamlit web interface."""
    import streamlit.web.cli as stcli
    import sys
    
    sys.argv = ["streamlit", "run", __file__, "--server.port", str(port)]
    sys.exit(stcli.main())


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Code Review Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .issue-card {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .suggestion-card {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Code Review Agent</h1>', unsafe_allow_html=True)
    st.markdown("### Intelligent code analysis and algorithm optimization")
    
    # Check for API key in environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Show API key status
        st.success("✅ API Key loaded from environment")
        
        # Analysis type
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Repository Analysis", "File Analysis", "Algorithm Suggestions", "Interactive Chat"]
        )
        
        st.markdown("---")
        st.markdown("### 📊 Features")
        st.markdown("• **Multi-language Support**")
        st.markdown("• **Quality Analysis**")
        st.markdown("• **Algorithm Optimization**")
        st.markdown("• **Git Integration**")
        st.markdown("• **Real-time Feedback**")
    
    # Main content
    if analysis_type == "Repository Analysis":
        _repository_analysis_page(api_key)
    elif analysis_type == "File Analysis":
        _file_analysis_page(api_key)
    elif analysis_type == "Algorithm Suggestions":
        _algorithm_suggestions_page(api_key)
    elif analysis_type == "Interactive Chat":
        _interactive_chat_page(api_key)


def _repository_analysis_page(api_key: str):
    """Repository analysis page."""
    st.header("📁 Repository Analysis")
    st.markdown("Analyze code changes in a git repository for quality issues and improvements.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        repo_path = st.text_input(
            "Repository Path",
            placeholder="Enter a local path or a public GitHub URL",
            help="Enter a local path or a public GitHub URL"
        )
    
    with col2:
        commit_range = st.text_input(
            "Commit Range (Optional)",
            placeholder="HEAD~5..HEAD",
            help="Git commit range to analyze (e.g., HEAD~5..HEAD, main..feature)"
        )
    
    if st.button("🔍 Analyze Repository", type="primary"):
        if not repo_path:
            st.error("❌ Repository path is required")
            return
        
        temp_dir = None
        try:
            with st.spinner("🔍 Analyzing repository..."):
                agent = CodeReviewAgent(api_key)
                if is_github_url(repo_path):
                    try:
                        temp_dir = clone_github_repo(repo_path)
                        analysis_path = temp_dir
                    except Exception as e:
                        st.error(f"❌ Failed to clone repo: {e}")
                        return
                else:
                    analysis_path = repo_path
                
                result = asyncio.run(agent.analyze_repository(analysis_path))
                
                # Defensive check
                if isinstance(result, str):
                    st.error(f"❌ Error: {result}")
                    return
                
                if "error" in result:
                    st.error(f"❌ Analysis failed: {result['error']}")
                    return
                
                _display_repository_results(result)
                
                # After analysis, clean up if needed
                if is_github_url(repo_path):
                    shutil.rmtree(temp_dir, onerror=on_rm_error)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def _file_analysis_page(api_key: str):
    """File analysis page."""
    st.header("📄 File Analysis")
    st.markdown("Analyze a single file for code quality issues and improvements.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file to analyze",
        type=['py', 'js', 'java', 'cpp', 'c', 'go', 'rs', 'php', 'rb', 'ts', 'jsx', 'tsx'],
        help="Upload a code file to analyze"
    )
    
    # Or file path input
    file_path = st.text_input(
        "Or enter file path",
        placeholder="/path/to/your/file.py",
        help="Path to the file to analyze"
    )
    
    language = st.selectbox(
        "Programming Language (Auto-detected if not specified)",
        ["Auto-detect", "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "Go", "Rust", "PHP", "Ruby"]
    )
    
    if st.button("🔍 Analyze File", type="primary"):
        if not uploaded_file and not file_path:
            st.error("❌ Please upload a file or provide a file path")
            return
        
        with st.spinner("🔍 Analyzing file..."):
            try:
                agent = CodeReviewAgent(api_key)
                
                if uploaded_file:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    result = asyncio.run(agent.analyze_file_with_llm(tmp_file_path, language if language != "Auto-detect" else None))
                    
                    # Clean up
                    Path(tmp_file_path).unlink()
                else:
                    result = asyncio.run(agent.analyze_file_with_llm(file_path, language if language != "Auto-detect" else None))
                
                if "error" in result:
                    st.error(f"❌ Analysis failed: {result['error']}")
                    return
                
                _display_file_results(result)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def _algorithm_suggestions_page(api_key: str):
    """Algorithm suggestions page."""
    st.header("🚀 Algorithm Suggestions")
    st.markdown("Get suggestions for more efficient algorithms and optimizations.")
    
    # Code input
    code = st.text_area(
        "Enter your code",
        height=300,
        placeholder="def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr",
        help="Paste your code here for algorithm analysis"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "Go", "Rust", "PHP", "Ruby"]
        )
    
    with col2:
        task_description = st.text_input(
            "Task Description (Optional)",
            placeholder="What is this code trying to accomplish?",
            help="Describe what the code is supposed to do"
        )
    
    if st.button("🚀 Analyze Algorithms", type="primary"):
        if not code.strip():
            st.error("❌ Please enter some code to analyze")
            return
        
        with st.spinner("🚀 Analyzing algorithms..."):
            try:
                agent = CodeReviewAgent(api_key)
                result = asyncio.run(agent.tools.suggest_algorithms(code, language, task_description))
                
                if "error" in result:
                    st.error(f"❌ Analysis failed: {result['error']}")
                    return
                
                _display_algorithm_results(result, code, language)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def _interactive_chat_page(api_key: str):
    """Interactive chat page."""
    st.header("💬 Interactive Chat")
    st.markdown("Chat with the AI agent for code review and suggestions.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about code review, algorithms, or any coding questions..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                try:
                    agent = CodeReviewAgent(api_key)
                    response = asyncio.run(agent.send_message(prompt))
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def _display_repository_results(result: dict):
    """Display repository analysis results."""
    st.success("✅ Analysis complete!")
    
    st.write("### Summary")
    st.json(result.get("summary", {}))
    if result.get("errors"):
        st.warning("Some files could not be analyzed:")
        for err in result["errors"]:
            st.error(f"{err['file']}: {err['error']}")
    
    st.write("### Code Review Analyses")
    for analysis in result.get("analyses", []):
        st.subheader(f"File: {analysis['file']}")
        if 'analysis' in analysis:
            st.markdown(analysis['analysis'])
        else:
            st.error(f"Error: {analysis['error']}")


def _display_file_results(result: dict):
    """Display file analysis results."""
    st.success("✅ Analysis complete!")
    
    if "llm_analysis" in result:
        st.subheader("🤖 AI Code Review")
        st.markdown(result["llm_analysis"])
    
    # File info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("File Size", f"{result.get('size', 0):,} chars")
    
    with col2:
        st.metric("Lines of Code", result.get("lines", 0))
    
    with col3:
        st.metric("Language", result.get("language", "Unknown"))
    
    # Issues
    issues = result.get("issues", [])
    if issues:
        st.subheader("⚠️ Issues Found")
        for issue in issues:
            severity = issue.get("severity", "unknown").upper()
            if severity in ["CRITICAL", "HIGH"]:
                st.error(f"**{severity}:** {issue.get('description', 'No description')}")
            elif severity == "MEDIUM":
                st.warning(f"**{severity}:** {issue.get('description', 'No description')}")
            else:
                st.info(f"**{severity}:** {issue.get('description', 'No description')}")
    
    # Suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        st.subheader("💡 Suggestions")
        for suggestion in suggestions:
            st.info(f"• {suggestion.get('description', 'No description')}")


def _display_algorithm_results(result: dict, original_code: str, language: str):
    """Display algorithm analysis results."""
    st.success("✅ Algorithm analysis complete!")
    
    # Original code
    st.subheader("📝 Original Code")
    try:
        lexer = get_lexer_by_name(language.lower())
        highlighted_code = highlight(original_code, lexer, HtmlFormatter())
        st.markdown(highlighted_code, unsafe_allow_html=True)
    except:
        st.code(original_code, language=language.lower())
    
    # Current complexity
    complexity = result.get("current_complexity", {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Time Complexity", complexity.get("time_complexity", "Unknown"))
    
    with col2:
        st.metric("Space Complexity", complexity.get("space_complexity", "Unknown"))
    
    # Suggestions
    suggestions = result.get("suggestions", [])
    if suggestions:
        st.subheader("💡 Suggestions")
        for suggestion in suggestions:
            priority = suggestion.get("priority", "medium").upper()
            if priority == "HIGH":
                st.error(f"**{priority}:** {suggestion.get('description', 'No description')}")
            elif priority == "MEDIUM":
                st.warning(f"**{priority}:** {suggestion.get('description', 'No description')}")
            else:
                st.info(f"**{priority}:** {suggestion.get('description', 'No description')}")
    
    # Improved algorithms
    improved = result.get("improved_algorithms", [])
    if improved:
        st.subheader("🔄 Improved Algorithms")
        for algo in improved:
            with st.expander(f"📊 {algo.get('pattern', 'Unknown pattern')}"):
                st.write(f"**Current:** {algo.get('current', 'Unknown')}")
                st.write(f"**Suggestion:** {algo.get('suggestion', 'No suggestion')}")
                if "example" in algo:
                    st.code(algo["example"], language=language.lower())


def is_github_url(url):
    return re.match(r'https://github.com/.+/.+', url)


def clone_github_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir


if __name__ == "__main__":
    main() 