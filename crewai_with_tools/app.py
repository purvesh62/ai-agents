from datetime import datetime
from crew_agent.composio_crew import ComposioAgentCrew
from crew_agent.storage_manager import StorageManager
from crew_agent.output_models import CrewExecutionResult, TokenUsage
import uuid


def parse_task_outputs(crew_output) -> tuple[dict, dict]:
    """
    Parse individual task outputs from crew execution

    Args:
        crew_output: The output from crew.kickoff()

    Returns:
        Tuple of (task_outputs with pydantic models, raw_outputs)
    """
    task_outputs = {}
    raw_outputs = {}

    # Extract task outputs if available
    if hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
        for task_output in crew_output.tasks_output:
            task_name = task_output.name if hasattr(task_output, 'name') else "unknown"

            # Get raw output
            output_str = str(task_output.raw) if hasattr(task_output, 'raw') else str(task_output)
            raw_outputs[task_name] = output_str

            # Get pydantic output if available
            if hasattr(task_output, 'pydantic') and task_output.pydantic:
                task_outputs[task_name] = task_output.pydantic
            elif hasattr(task_output, 'output_pydantic') and task_output.output_pydantic:
                task_outputs[task_name] = task_output.output_pydantic

    return task_outputs, raw_outputs


def extract_token_usage(crew_output) -> tuple[TokenUsage, dict]:
    """
    Extract token usage information from crew output

    Args:
        crew_output: The output from crew.kickoff()

    Returns:
        Tuple of (total_token_usage, task_token_usage_dict)
    """
    total_usage = TokenUsage(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        model_name="claude-sonnet-4-5-20250929"
    )

    task_usage = {}

    # Extract token usage if available
    if hasattr(crew_output, 'token_usage'):
        usage = crew_output.token_usage
        if isinstance(usage, dict):
            total_usage = TokenUsage(
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0),
                model_name=usage.get('model_name', 'claude-sonnet-4-5-20250929')
            )

    # Extract per-task usage if available
    if hasattr(crew_output, 'tasks_output') and crew_output.tasks_output:
        for task_output in crew_output.tasks_output:
            task_name = task_output.name if hasattr(task_output, 'name') else "unknown"
            if hasattr(task_output, 'token_usage'):
                usage = task_output.token_usage
                if isinstance(usage, dict):
                    task_usage[task_name] = TokenUsage(
                        prompt_tokens=usage.get('prompt_tokens', 0),
                        completion_tokens=usage.get('completion_tokens', 0),
                        total_tokens=usage.get('total_tokens', 0),
                        model_name=usage.get('model_name', 'claude-sonnet-4-5-20250929')
                    )

    return total_usage, task_usage


def run_crew_agent():
    """Main function with storage manager integration"""
    print("\n" + "=" * 60)
    print("🚀 Starting Composio Crew")
    print("=" * 60 + "\n")

    # Prepare input data
    current_date = datetime.now().strftime("%Y-%m-%d")
    input_data = {
        "current_date": current_date,
    }

    # Execute crew
    print("⏳ Running crew tasks...")
    crew_result = ComposioAgentCrew().crew().kickoff(input_data)

    print("\n" + "=" * 60)
    print("🧠 Composio Crew Result")
    print("=" * 60)
    print(crew_result)
    print("\n")

    # Initialize storage manager
    storage_manager = StorageManager(base_output_dir="outputs")

    # Generate execution ID
    execution_id = str(uuid.uuid4())

    # Parse outputs
    task_outputs, raw_outputs = parse_task_outputs(crew_result)

    # Extract token usage
    total_usage, task_usage = extract_token_usage(crew_result)

    # Map task names to outputs
    daily_calendar_output = task_outputs.get('daily_calendar_tasks') or task_outputs.get('daily_calendar')
    email_extraction_output = task_outputs.get('email_extraction_task') or task_outputs.get('email_extraction')
    summary_generator_output = task_outputs.get('summary_generator_task') or task_outputs.get('summary_generator')

    # Create execution result with structured outputs
    execution_result = CrewExecutionResult(
        execution_id=execution_id,
        timestamp=datetime.now(),
        daily_calendar_output=daily_calendar_output,
        email_extraction_output=email_extraction_output,
        summary_generator_output=summary_generator_output,
        total_token_usage=total_usage,
        task_token_usage=task_usage,
        metadata={
            "current_date": current_date,
            "agent_name": "personal_assistant",
            "status": "success",
            "final_output": str(crew_result),
            "tasks_completed": list(task_outputs.keys())
        }
    )

    # Save outputs
    print("💾 Saving outputs...")
    output_folder = storage_manager.save_crew_execution_result(
        folder_name="daily_assistant",
        execution_result=execution_result,
        raw_outputs=raw_outputs
    )

    print(f"✅ Outputs saved to: {output_folder}")
    print(f"📋 Execution ID: {execution_id}")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    run_crew_agent()
