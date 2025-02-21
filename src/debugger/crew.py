from typing import Dict, Any, Optional
from datetime import datetime
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase
from debugger.tools.custom_tool import code_analysis_tool, dependency_analyzer_tool, solution_validator_tool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class Debugger():
	"""AI Debugging Crew for analyzing and fixing code issues"""

	def _validate_inputs(self, inputs: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
		"""Validate and preprocess inputs before the crew starts."""
		if inputs is None:
			return None
			
		required_fields = ['code_issue', 'code_context', 'project_path']
		for field in required_fields:
			if field not in inputs:
				raise ValueError(f"{field} is required")
		
		# Add additional context
		inputs['timestamp'] = datetime.now().isoformat()
		return inputs

	def _format_results(self, result: str) -> str:
		"""Format the results after the crew completes."""
		return f"""
# Debugging Analysis Results
Generated on: {datetime.now().isoformat()}

## Code Issue
{result}

## Analysis Files
- Root Cause Analysis: output/root_cause_analysis.md
- Solution Proposals: output/solution_proposals.md
- Solution Evaluation: output/solution_evaluation.md
"""

	def _create_agents(self):
		"""Create the debugging agents."""
		self.rca_agent = Agent(
			role="Root Cause Analysis Expert",
			goal="Analyze code issues deeply to identify the root cause of bugs and problems",
			backstory="""An expert debugger with years of experience in analyzing complex software systems 
			and identifying root causes of issues. Skilled at tracing code execution paths and understanding 
			system interactions.""",
			tools=[code_analysis_tool, dependency_analyzer_tool],
			verbose=True
		)

		self.solution_generator = Agent(
			role="Solution Architect",
			goal="Generate multiple viable solutions for identified code issues",
			backstory="""A creative problem solver with extensive experience in software design patterns 
			and best practices. Capable of developing multiple approaches to solve complex technical problems.""",
			tools=[code_analysis_tool],
			verbose=True
		)

		self.solution_evaluator = Agent(
			role="Solution Evaluator",
			goal="Evaluate and rank proposed solutions based on effectiveness, maintainability, and performance",
			backstory="""An experienced technical lead who specializes in code review and quality assessment. 
			Expert at analyzing trade-offs between different implementation approaches.""",
			tools=[solution_validator_tool],
			verbose=True
		)

		return [self.rca_agent, self.solution_generator, self.solution_evaluator]

	def _create_tasks(self):
		"""Create the debugging tasks."""
		analyze_task = Task(
			description="""
			Analyze the code issue to identify root causes. Consider:
			1. Code structure and patterns
			2. Potential bugs and anti-patterns
			3. Dependencies and interactions
			4. Impact on system stability
			
			Use the code_analysis tool with the actual code from the 'code_context' input.
			Use the dependency_analyzer tool with the 'project_path' input.
			""",
			agent=self.rca_agent,
			expected_output="A detailed analysis of the root cause including affected components and error patterns",
			output_file="output/root_cause_analysis.md"
		)

		generate_task = Task(
			description="""
			Generate multiple solutions for the identified issues. For each solution:
			1. Provide detailed implementation steps
			2. List required code changes
			3. Consider best practices and patterns
			4. Evaluate implementation complexity
			
			Use the code_analysis tool to validate your proposed solutions.
			""",
			agent=self.solution_generator,
			context=[analyze_task],
			expected_output="Multiple solution proposals with implementation steps and trade-offs",
			output_file="output/solution_proposals.md"
		)

		evaluate_task = Task(
			description="""
			Evaluate and rank the proposed solutions based on:
			1. Code quality and maintainability
			2. Performance impact
			3. Implementation effort
			4. Potential risks and trade-offs
			
			Use the solution_validator tool to check each proposed solution.
			""",
			agent=self.solution_evaluator,
			context=[generate_task],
			expected_output="A ranked list of solutions with detailed evaluation",
			output_file="output/solution_evaluation.md"
		)

		return [analyze_task, generate_task, evaluate_task]

	def run(self, inputs: Dict[str, Any]) -> str:
		"""Run the debugging crew with input validation and result formatting."""
		validated_inputs = self._validate_inputs(inputs)
		
		# Create agents and tasks
		agents = self._create_agents()
		tasks = self._create_tasks()
		
		# Create and run the crew
		crew = Crew(
			agents=agents,
			tasks=tasks,
			process=Process.sequential,
			verbose=True
		)
		
		result = crew.kickoff(inputs=validated_inputs)
		return self._format_results(result)
