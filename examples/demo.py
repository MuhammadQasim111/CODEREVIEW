"""Demo script for the AI Code Review Agent."""

import asyncio
import os
from pathlib import Path

# Add the src directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codereview.agent import CodeReviewAgent


async def demo_algorithm_suggestions():
    """Demo algorithm suggestions feature."""
    print("🚀 Demo: Algorithm Suggestions")
    print("=" * 50)
    
    # Example inefficient code
    inefficient_code = """
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    
    try:
        agent = CodeReviewAgent()
        result = await agent.tools.suggest_algorithms(
            code=inefficient_code,
            language="python",
            task_description="Find duplicates in an array and sort the array"
        )
        
        print("✅ Algorithm analysis complete!")
        print(f"Current Time Complexity: {result.get('current_complexity', {}).get('time_complexity', 'Unknown')}")
        print(f"Current Space Complexity: {result.get('current_complexity', {}).get('space_complexity', 'Unknown')}")
        
        suggestions = result.get("suggestions", [])
        if suggestions:
            print(f"\n💡 Found {len(suggestions)} suggestions:")
            for suggestion in suggestions:
                print(f"  • {suggestion.get('description', 'No description')}")
        
        improved = result.get("improved_algorithms", [])
        if improved:
            print(f"\n🔄 Found {len(improved)} algorithm improvements:")
            for algo in improved:
                print(f"  • {algo.get('pattern', 'Unknown')}: {algo.get('suggestion', 'No suggestion')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


async def demo_file_analysis():
    """Demo file analysis feature."""
    print("\n📄 Demo: File Analysis")
    print("=" * 50)
    
    # Create a sample file to analyze
    sample_code = """
import os

def process_files(directory):
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                files.append(content)
    return files

def calculate_average(numbers):
    total = 0
    count = 0
    for num in numbers:
        total = total + num
        count = count + 1
    return total / count

class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, name, email, password):
        user = {"name": name, "email": email, "password": password}
        self.users.append(user)
    
    def find_user_by_email(self, email):
        for user in self.users:
            if user["email"] == email:
                return user
        return None
"""
    
    # Write to temporary file
    temp_file = Path("temp_demo.py")
    temp_file.write_text(sample_code)
    
    try:
        agent = CodeReviewAgent()
        result = await agent.tools.analyze_file(str(temp_file), "python")
        
        print("✅ File analysis complete!")
        print(f"File: {result.get('file_path', 'Unknown')}")
        print(f"Language: {result.get('language', 'Unknown')}")
        print(f"Size: {result.get('size', 0)} characters, {result.get('lines', 0)} lines")
        
        issues = result.get("issues", [])
        if issues:
            print(f"\n⚠️  Found {len(issues)} issues:")
            for issue in issues:
                severity = issue.get("severity", "unknown").upper()
                print(f"  [{severity}] {issue.get('description', 'No description')}")
        
        suggestions = result.get("suggestions", [])
        if suggestions:
            print(f"\n💡 Found {len(suggestions)} suggestions:")
            for suggestion in suggestions:
                print(f"  • {suggestion.get('description', 'No description')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()


async def demo_interactive_chat():
    """Demo interactive chat feature."""
    print("\n💬 Demo: Interactive Chat")
    print("=" * 50)
    print("This would launch the interactive chat interface.")
    print("In a real scenario, you would use: python -m codereview interactive")
    
    # Example of how to use the chat programmatically
    try:
        agent = CodeReviewAgent()
        
        # Create assistant and thread
        await agent.create_assistant()
        await agent.create_thread()
        
        # Send a message
        response = await agent.send_message(
            "Can you suggest a more efficient way to find duplicates in a Python list?"
        )
        
        print("🤖 AI Response:")
        print(response)
    
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all demos."""
    print("🤖 AI Code Review Agent - Demo")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY=your_api_key_here")
        return
    
    # Run demos
    await demo_algorithm_suggestions()
    await demo_file_analysis()
    await demo_interactive_chat()
    
    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("\nTo try the full interfaces:")
    print("  • CLI: python -m codereview")
    print("  • Web: python -m codereview web")
    print("  • Interactive: python -m codereview interactive")


if __name__ == "__main__":
    asyncio.run(main()) 