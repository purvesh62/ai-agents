from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Individual Task Output Models

class CalendarEvent(BaseModel):
    """Model for a single calendar event"""
    title: str
    date_time: Optional[str] = None
    participants: Optional[List[str]] = None
    agenda: Optional[str] = None
    location: Optional[str] = None
    event_type: Optional[str] = None  # meeting, birthday, special event


class DailyCalendarOutput(BaseModel):
    """Output model for daily_calendar_tasks"""
    events: List[CalendarEvent]
    special_events: Optional[List[CalendarEvent]] = None
    todo_list: Optional[List[str]] = None
    summary: str


class Email(BaseModel):
    """Model for a single email"""
    sender: str
    subject: str
    date_received: str
    content_overview: str
    email_type: Optional[str] = None  # unread, newsletter, promotional


class EmailExtractionOutput(BaseModel):
    """Output model for email_extraction_task"""
    unread_emails: List[Email]
    newsletters: List[Email]
    promotional_emails: List[Email]
    summary: Optional[str] = None


class SummaryGeneratorOutput(BaseModel):
    """Output model for summary_generator_task"""
    key_meetings: List[str]
    important_emails: List[str]
    action_items: List[str]
    personal_events: Optional[List[str]] = None
    newsletter_summaries: Optional[List[str]] = None
    google_docs_url: Optional[str] = None
    full_summary: str


# Metadata and Execution Tracking

class TokenUsage(BaseModel):
    """Model for tracking token usage"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model_name: Optional[str] = None


class ExecutionMetadata(BaseModel):
    """Metadata for each execution"""
    execution_id: str
    timestamp: datetime
    current_date: str
    task_name: str
    agent_name: str
    status: str  # success, failed, partial
    error_message: Optional[str] = None


class CrewExecutionResult(BaseModel):
    """Complete execution result with all task outputs"""
    execution_id: str
    timestamp: datetime
    daily_calendar_output: Optional[DailyCalendarOutput] = None
    email_extraction_output: Optional[EmailExtractionOutput] = None
    summary_generator_output: Optional[SummaryGeneratorOutput] = None
    total_token_usage: TokenUsage
    task_token_usage: dict = Field(default_factory=dict)  # task_name -> TokenUsage
    metadata: dict = Field(default_factory=dict)
