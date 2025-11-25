import os
import agentops
from crewai import Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Task, Crew
from composio_crewai import Action, ComposioToolSet
from crew_agent.output_models import (
    DailyCalendarOutput,
    EmailExtractionOutput,
    SummaryGeneratorOutput
)


def load_llm(model_name: str) -> LLM | None:
    try:
        return LLM(
            model=model_name,
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url='https://openrouter.ai/api/v1',
            temperature=0.7,
            additional_params={
                "default_headers": {
                    "HTTP-Referer": "https://purvesh.me",
                    "X-Title": "CrewAI App"
                }
            }
        )
    except Exception as e:
        print(f"Error loading LLM for model {model_name}: {str(e)}")
        return None


"""
OpenAI Model
"""
# OPENAI_MODEL = 'openrouter/openai/gpt-5-mini-2025-08-07'
OPENAI_MODEL = 'openrouter/openai/gpt-5.1'
openai = load_llm(OPENAI_MODEL)

"""
Anthropic Model
"""

CLAUDE_MODEL = 'openrouter/anthropic/claude-sonnet-4-5-20250929'
# CLAUDE_MODEL = 'openrouter/anthropic/claude-opus-4.5'
claude = load_llm(CLAUDE_MODEL)
claude_base = LLM(model='claude-sonnet-4-5-20250929', api_key=os.getenv('ANTHROPIC_API_KEY'))

"""
Gemini Model
"""
# GEMINI_MODEL = 'openrouter/google/gemini-3-pro-preview'
GEMINI_MODEL = 'openrouter/google/gemini-2.5-pro'
# GEMINI_MODEL = 'openrouter/google/gemini-2.5-flash'
gemini = load_llm(GEMINI_MODEL)

# Initialize AgentOps
agentops.init()

toolset = ComposioToolSet(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    # entity_id='pg-test-e525fc15-0c7d-4daa-bc45-4a90667f4493'
    entity_id='purvesh62@gmail.com'
)

tools = toolset.get_tools(
    actions=[
        # Google Calendar
        Action.GOOGLECALENDAR_FIND_EVENT,
        Action.GOOGLECALENDAR_GET_CALENDAR,

        # Gmail
        Action.GMAIL_FETCH_EMAILS,

        # Notion
        # Action.NOTION_ADD_PAGE_CONTENT,
        # Action.NOTION_CREATE_COMMENT,
        # Action.NOTION_DELETE_BLOCK,
        # Action.NOTION_INSERT_ROW_DATABASE,

        # Google Docs
        Action.GOOGLEDOCS_CREATE_DOCUMENT,
        Action.GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN,
        # Action.GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN,
        # Action.GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT,
        # Action.GOOGLEDOCS_GET_DOCUMENT_BY_ID
    ]
)


@CrewBase
class ComposioAgentCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def personal_assistant(self) -> Agent:
        return Agent(
            config=self.agents_config['personal_assistant'],
            llm=claude_base,
            verbose=True,
            memory=False,
            tools=tools,
        )

    @agent
    def email_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['email_manager'],
            llm=claude_base,
            verbose=True,
            memory=False,
            tools=tools,
        )

    @task
    def daily_calendar_tasks(self) -> Task:
        return Task(
            config=self.tasks_config['daily_calendar_tasks'],
            agent=self.personal_assistant(),
            output_pydantic=DailyCalendarOutput,
        )

    @task
    def email_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['email_extraction_task'],
            agent=self.email_manager(),
            context=[self.daily_calendar_tasks()],
            output_pydantic=EmailExtractionOutput,
        )

    @task
    def summary_generator_task(self) -> Task:
        return Task(
            config=self.tasks_config['summary_generator_task'],
            agent=self.personal_assistant(),
            context=[self.email_extraction_task()],
            output_pydantic=SummaryGeneratorOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
