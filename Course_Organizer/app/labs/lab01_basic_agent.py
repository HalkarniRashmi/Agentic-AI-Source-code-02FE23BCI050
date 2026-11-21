"""
LAB 1 - BASIC AGENT
Run from the project root:
    python -m app.labs.lab01_basic_agent
"""

import json
from app.agents.base_agent import BaseAgent


class BasicAcademicAgent(BaseAgent):
    """Minimal agent demonstrating the basic execution lifecycle."""

    def __init__(self):
        super().__init__(
            name="AcademicFlow Basic Agent",
            description="Demonstrates the basic agent execution lifecycle."
        )

    def execute(self, input_data):
        task = input_data.get("task", "general_academic_assistance")
        user_id = input_data.get("user_id")

        if not isinstance(task, str) or not task.strip():
            raise ValueError("A non-empty task is required.")

        return {
            "message": "Hello! I am the AcademicFlow Basic Agent.",
            "task_received": task,
            "user_id": user_id,
            "result": "Basic agent executed successfully."
        }


def run_lab():
    print("=" * 60)
    print("             LAB 1 - BASIC AGENT")
    print("=" * 60)

    agent = BasicAcademicAgent()
    request = {
        "task": "Introduce yourself and demonstrate basic execution",
        "user_id": 1
    }

    print("\n[1] AGENT DETAILS")
    print("Agent:", agent.name)
    print("Description:", agent.description)

    print("\n[2] INPUT")
    print(json.dumps(request, indent=4))

    print("\n[3] RUNNING AGENT")
    result = agent.run(request)

    print("\n[4] EXECUTION RESULT")
    print(json.dumps(result, indent=4, ensure_ascii=False, default=str))

    print("\n" + "=" * 60)
    print("          LAB 1 EXECUTION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_lab()
    except Exception as error:
        print("\n[LAB 1 ERROR]", error)
