import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

from crew_agent.output_models import (
    CrewExecutionResult,
    DailyCalendarOutput,
    EmailExtractionOutput,
    SummaryGeneratorOutput,
    TokenUsage,
    ExecutionMetadata
)


class StorageManager:
    """Manages storage of CrewAI execution outputs"""

    def __init__(self, base_output_dir: str = "outputs"):
        """
        Initialize the storage manager

        Args:
            base_output_dir: Base directory for storing outputs (default: "outputs")
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)

    def create_execution_folder(self, folder_name: str) -> tuple[str, Path]:
        """
        Create a unique folder for an execution with UUID

        Args:
            folder_name: Name prefix for the folder

        Returns:
            Tuple of (execution_id, folder_path)
        """
        execution_id = str(uuid.uuid4())
        folder_path = self.base_output_dir / f"{folder_name}_{execution_id}"
        folder_path.mkdir(parents=True, exist_ok=True)
        return execution_id, folder_path

    def save_task_output(
        self,
        folder_path: Path,
        task_name: str,
        output_data: BaseModel,
        raw_output: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save task output in both JSON and Markdown formats

        Args:
            folder_path: Path to the execution folder
            task_name: Name of the task
            output_data: Pydantic model containing the structured output
            raw_output: Raw string output from the task

        Returns:
            Dictionary with paths to saved files
        """
        saved_files = {}

        # Save JSON output
        json_path = folder_path / f"{task_name}_output.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data.model_dump(), f, indent=2, default=str)
        saved_files['json'] = str(json_path)

        # Save Markdown output
        md_path = folder_path / f"{task_name}_output.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {task_name.replace('_', ' ').title()}\n\n")
            f.write(f"**Generated at:** {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")

            # Write structured data
            f.write("## Structured Output\n\n")
            f.write(self._format_model_as_markdown(output_data))

            # Write raw output if available
            if raw_output:
                f.write("\n\n---\n\n")
                f.write("## Raw Output\n\n")
                f.write(raw_output)

        saved_files['markdown'] = str(md_path)

        return saved_files

    def save_token_usage(
        self,
        folder_path: Path,
        task_token_usage: Dict[str, TokenUsage],
        total_token_usage: TokenUsage
    ):
        """
        Save token usage information to JSON file

        Args:
            folder_path: Path to the execution folder
            task_token_usage: Dictionary mapping task names to their token usage
            total_token_usage: Total token usage across all tasks
        """
        token_data = {
            "total_usage": total_token_usage.model_dump(),
            "task_usage": {
                task_name: usage.model_dump()
                for task_name, usage in task_token_usage.items()
            },
            "timestamp": datetime.now().isoformat()
        }

        token_path = folder_path / "token_usage.json"
        with open(token_path, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2)

    def save_execution_metadata(
        self,
        folder_path: Path,
        execution_id: str,
        metadata: Dict[str, Any]
    ):
        """
        Save execution metadata to JSON file

        Args:
            folder_path: Path to the execution folder
            execution_id: Unique execution ID
            metadata: Dictionary containing execution metadata
        """
        metadata_data = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }

        metadata_path = folder_path / "execution_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_data, f, indent=2, default=str)

    def save_crew_execution_result(
        self,
        folder_name: str,
        execution_result: CrewExecutionResult,
        raw_outputs: Optional[Dict[str, str]] = None
    ) -> Path:
        """
        Complete workflow to save all execution results

        Args:
            folder_name: Name prefix for the output folder
            execution_result: Complete execution result with all outputs
            raw_outputs: Dictionary mapping task names to raw string outputs

        Returns:
            Path to the created folder
        """
        execution_id, folder_path = self.create_execution_folder(folder_name)
        raw_outputs = raw_outputs or {}

        # Save individual task outputs
        if execution_result.daily_calendar_output:
            self.save_task_output(
                folder_path,
                "daily_calendar",
                execution_result.daily_calendar_output,
                raw_outputs.get("daily_calendar")
            )

        if execution_result.email_extraction_output:
            self.save_task_output(
                folder_path,
                "email_extraction",
                execution_result.email_extraction_output,
                raw_outputs.get("email_extraction")
            )

        if execution_result.summary_generator_output:
            self.save_task_output(
                folder_path,
                "summary_generator",
                execution_result.summary_generator_output,
                raw_outputs.get("summary_generator")
            )

        # Save token usage
        self.save_token_usage(
            folder_path,
            execution_result.task_token_usage,
            execution_result.total_token_usage
        )

        # Save execution metadata
        self.save_execution_metadata(
            folder_path,
            execution_id,
            execution_result.metadata
        )

        # Save complete execution result
        complete_result_path = folder_path / "complete_execution_result.json"
        with open(complete_result_path, 'w', encoding='utf-8') as f:
            json.dump(execution_result.model_dump(), f, indent=2, default=str)

        return folder_path

    def _format_model_as_markdown(self, model: BaseModel, indent: int = 0) -> str:
        """
        Format a Pydantic model as Markdown

        Args:
            model: Pydantic model to format
            indent: Indentation level

        Returns:
            Formatted Markdown string
        """
        lines = []
        indent_str = "  " * indent

        for field_name, field_value in model.model_dump().items():
            formatted_name = field_name.replace('_', ' ').title()

            if isinstance(field_value, list):
                if not field_value:
                    continue
                lines.append(f"{indent_str}- **{formatted_name}:**")
                for item in field_value:
                    if isinstance(item, dict):
                        lines.append(f"{indent_str}  - {self._format_dict_as_markdown(item, indent + 2)}")
                    else:
                        lines.append(f"{indent_str}  - {item}")
            elif isinstance(field_value, dict):
                if not field_value:
                    continue
                lines.append(f"{indent_str}- **{formatted_name}:**")
                lines.append(self._format_dict_as_markdown(field_value, indent + 1))
            elif field_value is not None:
                lines.append(f"{indent_str}- **{formatted_name}:** {field_value}")

        return "\n".join(lines)

    def _format_dict_as_markdown(self, data: dict, indent: int = 0) -> str:
        """Format a dictionary as Markdown"""
        lines = []
        indent_str = "  " * indent

        for key, value in data.items():
            formatted_key = str(key).replace('_', ' ').title()

            if isinstance(value, (list, dict)):
                lines.append(f"{indent_str}- **{formatted_key}:** {json.dumps(value, indent=2)}")
            elif value is not None:
                lines.append(f"{indent_str}- **{formatted_key}:** {value}")

        return "\n".join(lines)


def create_sample_execution_result() -> CrewExecutionResult:
    """
    Create a sample execution result for testing

    Returns:
        Sample CrewExecutionResult
    """
    from crew_agent.output_models import CalendarEvent, Email

    execution_id = str(uuid.uuid4())

    # Sample calendar output
    calendar_output = DailyCalendarOutput(
        events=[
            CalendarEvent(
                title="Team Standup",
                date_time="2025-11-25 10:00 AM",
                participants=["John", "Sarah", "Mike"],
                agenda="Daily sync",
                location="Zoom",
                event_type="meeting"
            )
        ],
        special_events=[],
        todo_list=["Review PR", "Update documentation"],
        summary="One meeting scheduled for today"
    )

    # Sample email output
    email_output = EmailExtractionOutput(
        unread_emails=[
            Email(
                sender="boss@company.com",
                subject="Project Update",
                date_received="2025-11-25",
                content_overview="Need status update on the project",
                email_type="unread"
            )
        ],
        newsletters=[],
        promotional_emails=[],
        summary="1 unread email requiring attention"
    )

    # Sample summary output
    summary_output = SummaryGeneratorOutput(
        key_meetings=["Team Standup at 10:00 AM"],
        important_emails=["Project Update from boss"],
        action_items=["Provide project status update", "Review PR"],
        personal_events=[],
        newsletter_summaries=[],
        full_summary="Today you have 1 meeting and 1 important email to address"
    )

    # Token usage
    total_usage = TokenUsage(
        prompt_tokens=1500,
        completion_tokens=800,
        total_tokens=2300,
        model_name="claude-sonnet-4-5"
    )

    task_usage = {
        "daily_calendar": TokenUsage(prompt_tokens=500, completion_tokens=250, total_tokens=750),
        "email_extraction": TokenUsage(prompt_tokens=500, completion_tokens=300, total_tokens=800),
        "summary_generator": TokenUsage(prompt_tokens=500, completion_tokens=250, total_tokens=750)
    }

    return CrewExecutionResult(
        execution_id=execution_id,
        timestamp=datetime.now(),
        daily_calendar_output=calendar_output,
        email_extraction_output=email_output,
        summary_generator_output=summary_output,
        total_token_usage=total_usage,
        task_token_usage=task_usage,
        metadata={
            "current_date": "2025-11-25",
            "agent_name": "personal_assistant",
            "status": "success"
        }
    )


# Example usage
if __name__ == "__main__":
    # Create storage manager
    storage_mgr = StorageManager(base_output_dir="outputs")

    # Create sample execution result
    result = create_sample_execution_result()

    # Save all outputs
    output_folder = storage_mgr.save_crew_execution_result(
        folder_name="daily_assistant",
        execution_result=result,
        raw_outputs={
            "daily_calendar": "Raw output from calendar task...",
            "email_extraction": "Raw output from email task...",
            "summary_generator": "Raw output from summary task..."
        }
    )

    print(f"Outputs saved to: {output_folder}")