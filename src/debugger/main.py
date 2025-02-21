#!/usr/bin/env python
import sys
import warnings
import os
from pathlib import Path
from datetime import datetime
import traceback

from crewai import Crew, Process
from debugger.crew import Debugger

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the debugging crew.
    """
    # Example code with multiple issues
    sample_code = '''
    class DataProcessor:
        cache = []  # Global mutable state
        
        def process_data(self, data=[]):  # Mutable default argument
            try:
                DataProcessor.cache.append(data)  # Modifying global state
                result = data.process()  # Potential attribute error
                return result
            except:  # Bare except clause
                print("Error occurred")  # Poor error handling
                
        def get_cache():  # Missing self parameter
            return DataProcessor.cache
    '''
    
    inputs = {
        'code_issue': '''
        The code has multiple issues:
        1. Uses mutable default argument
        2. Modifies global state
        3. Has bare except clause
        4. Poor error handling
        5. Missing self parameter
        6. Potential attribute errors
        ''',
        'code_context': sample_code,
        'project_path': str(Path(os.getcwd()))
    }
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        print("\nStarting code analysis...")
        print("=" * 50)
        print("\nCode to analyze:")
        print(sample_code)
        print("\nIdentified issues:")
        print(inputs['code_issue'])
        print("=" * 50)
        
        # Initialize and run the debugging crew
        debugger = Debugger()
        result = debugger.run(inputs)
        
        # Save the final result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output_path = f"output/debug_result_{timestamp}.md"
        with open(final_output_path, 'w') as f:
            f.write(result)
        
        print("\nDebugging Analysis Results:")
        print(result)
        print(f"\nResults saved to: {final_output_path}")
        
    except ValueError as e:
        print(f"\nValidation Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError Details: {str(e)}")
        print("\nStacktrace:")
        traceback.print_exc()
        sys.exit(1)

def train():
    """
    Train the crew for a given number of iterations.
    """
    if len(sys.argv) < 3:
        print("Usage: python -m debugger.main train <n_iterations> <filename>")
        sys.exit(1)

    inputs = {
        'code_issue': 'Sample code issue with error handling',
        'code_context': 'def sample(): pass',
        'project_path': str(Path(os.getcwd()))
    }
    try:
        debugger = Debugger()
        agents = debugger._create_agents()
        tasks = debugger._create_tasks()
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
        crew.train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        print(f"\nError Details: {str(e)}")
        print("\nStacktrace:")
        traceback.print_exc()
        sys.exit(1)

def replay():
    """
    Replay the crew execution from a specific task.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m debugger.main replay <task_id>")
        sys.exit(1)

    try:
        debugger = Debugger()
        agents = debugger._create_agents()
        tasks = debugger._create_tasks()
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
        crew.replay(task_id=sys.argv[1])
    except Exception as e:
        print(f"\nError Details: {str(e)}")
        print("\nStacktrace:")
        traceback.print_exc()
        sys.exit(1)

def test():
    """
    Test the crew execution and returns the results.
    """
    if len(sys.argv) < 3:
        print("Usage: python -m debugger.main test <n_iterations> <model_name>")
        sys.exit(1)

    inputs = {
        'code_issue': 'Sample code issue with error handling',
        'code_context': 'def sample(): pass',
        'project_path': str(Path(os.getcwd()))
    }
    try:
        debugger = Debugger()
        agents = debugger._create_agents()
        tasks = debugger._create_tasks()
        crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
        crew.test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        print(f"\nError Details: {str(e)}")
        print("\nStacktrace:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        run()
