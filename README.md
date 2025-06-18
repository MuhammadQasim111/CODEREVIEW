# AI Code Review Agent

An intelligent code review agent built with OpenAI Agents SDK that analyzes code quality and suggests more efficient algorithms.

## Features

### 🤖 AI-Powered Code Analysis
- **Multi-language Support**: Python, JavaScript, Java, C++, Go, Rust, and more
- **Quality Dimensions**: Readability, Performance, Security, Maintainability, Best Practices
- **Git Integration**: Analyze code changes from git repositories
- **Real-time Feedback**: Interactive chat interface for code review

### 🚀 Algorithm Optimization
- **Complexity Analysis**: Time and space complexity evaluation
- **Efficiency Suggestions**: Identify inefficient patterns and suggest improvements
- **Alternative Algorithms**: Recommend better algorithms and data structures
- **Performance Comparison**: Compare current vs. optimized approaches

### 🛠️ Advanced Tools
- **File Analysis**: Analyze individual files for quality issues
- **Repository Analysis**: Review entire git repositories
- **Change Tracking**: Analyze specific commit ranges
- **Interactive Mode**: Chat-based interface for code review

### 🌐 Multiple Interfaces
- **CLI Interface**: Command-line tool for automation and power users
- **Web Interface**: Beautiful Streamlit web app for interactive use
- **Interactive Chat**: Real-time conversation with the AI agent

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd codereview
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   # Create a .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

## Usage

### 🌐 Web Interface (Recommended for most users)
Launch the beautiful Streamlit web interface:

```bash
# Method 1: Using the CLI command
codereview web

# Method 2: Direct module execution
python -m codereview web

# Method 3: Streamlit directly
streamlit run src/codereview/web.py
```

**Features of the Web Interface:**
- 📁 **Repository Analysis**: Upload or specify repository paths
- 📄 **File Analysis**: Upload individual files for review
- 🚀 **Algorithm Suggestions**: Paste code for optimization advice
- 💬 **Interactive Chat**: Real-time conversation with the AI
- 📊 **Visual Results**: Rich formatting, syntax highlighting, and metrics
- 🔧 **Easy Configuration**: Simple setup with API key input

### 💻 CLI Interface (For automation and power users)
Use the command-line interface for automation and integration:

```bash
# Interactive mode
codereview interactive

# Analyze a repository
codereview analyze --repo /path/to/repo

# Analyze specific commits
codereview analyze --repo /path/to/repo --commits HEAD~5..HEAD

# Analyze a single file
codereview analyze-file --file /path/to/file.py

# Get algorithm suggestions
codereview suggest-algorithms --code "your code here" --language python

# Save results to file
codereview analyze --repo /path/to/repo --output results.json
```

### 🎯 Quick Start Examples

#### Web Interface
1. Run `codereview web`
2. Open your browser to `http://localhost:8501`
3. Enter your OpenAI API key
4. Choose analysis type and upload/enter your code
5. Get instant feedback and suggestions!

#### CLI Interface
```bash
# Quick repository analysis
codereview analyze --repo ./my-project

# Interactive chat
codereview interactive

# Algorithm optimization
echo "def bubble_sort(arr): ..." | codereview suggest-algorithms --language python
```

## Example Interactions

### Repository Analysis
```
You: Please analyze the code changes in my repository at /path/to/my-project

🤖 Assistant: I'll analyze your repository for code quality issues and algorithm improvements...

📝 Analyzing commit: a1b2c3d4 - Add user authentication
📝 Analyzing commit: e5f6g7h8 - Implement search functionality

✅ Analysis complete! Found 3 critical issues and 8 suggestions for improvement.

**Critical Issues:**
1. Security vulnerability in user input validation (line 45)
2. Inefficient nested loop in search algorithm (line 78)
3. Memory leak in file handling (line 123)

**Algorithm Suggestions:**
- Replace O(n²) search with O(n log n) binary search
- Use hash maps for O(1) lookups instead of linear search
- Implement caching for repeated computations
```

### Algorithm Optimization
```
You: Can you suggest a more efficient algorithm for this sorting code?

🤖 Assistant: Looking at your sorting implementation...

**Current Analysis:**
- Time Complexity: O(n²) - Bubble sort implementation
- Space Complexity: O(1)
- Inefficient for large datasets

**Suggested Improvements:**

1. **Quick Sort** (O(n log n) average case):
   ```python
   def quick_sort(arr):
       if len(arr) <= 1:
           return arr
       pivot = arr[len(arr) // 2]
       left = [x for x in arr if x < pivot]
       middle = [x for x in arr if x == pivot]
       right = [x for x in arr if x > pivot]
       return quick_sort(left) + middle + quick_sort(right)
   ```

2. **Built-in Sort** (Optimized C implementation):
   ```python
   # Most efficient for Python
   arr.sort()  # in-place
   # or
   sorted_arr = sorted(arr)  # new list
   ```

3. **Heap Sort** for partial sorting:
   ```python
   import heapq
   # Get top 5 elements
   top_5 = heapq.nsmallest(5, arr)
   ```
```

## Interface Comparison

| Feature | Web Interface | CLI Interface |
|---------|---------------|---------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Visual Output** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **File Upload** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Automation** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **CI/CD Integration** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Resource Usage** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Quality Dimensions

The agent analyzes code across multiple dimensions:

### 📖 Readability
- Code clarity and structure
- Naming conventions
- Documentation quality
- Comment effectiveness

### ⚡ Performance
- Algorithm efficiency
- Resource usage
- Optimization opportunities
- Bottleneck identification

### 🔒 Security
- Input validation
- Authentication/authorization
- Data protection
- Common vulnerabilities

### 🔧 Maintainability
- Code organization
- Modularity
- Reusability
- Technical debt

### 📋 Best Practices
- Language-specific conventions
- Design patterns
- Error handling
- Testing practices

## Algorithm Suggestions

The agent specializes in identifying inefficient algorithms and suggesting improvements:

### Common Optimizations
- **Nested Loops**: Replace with more efficient algorithms
- **Linear Search**: Use hash maps or binary search
- **Redundant Computations**: Implement caching/memoization
- **Inefficient Data Structures**: Choose appropriate structures
- **Built-in Functions**: Leverage language optimizations

### Performance Improvements
- **Time Complexity**: Reduce from O(n²) to O(n log n) or O(n)
- **Space Complexity**: Minimize memory usage
- **Parallelization**: Use concurrent processing where applicable
- **Lazy Evaluation**: Defer computations until needed

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MODEL_NAME`: OpenAI model to use (default: gpt-4-turbo-preview)

### Customization
You can customize the agent's behavior by modifying:
- `src/codereview/prompts.py`: System prompts and analysis templates
- `src/codereview/tools.py`: Analysis tools and algorithms
- `src/codereview/agent.py`: Agent configuration and behavior
- `src/codereview/web.py`: Web interface customization
- `src/codereview/cli.py`: CLI interface customization

## Demo

Run the demo script to see the agent in action:

```bash
python examples/demo.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Review example usage in the tests

---

**Built with ❤️ using OpenAI Agents SDK**
