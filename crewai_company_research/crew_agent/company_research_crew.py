import os
import agentops
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ParallelSearchTool, SerperDevTool
from crewai import LLM

from crew_agent.output_models import (
    CompanyResearchData,
    CompanyResearchReport
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

agentops.init()


@CrewBase
class CompanyResearchCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def company_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['company_researcher'],
            llm=gemini,
            tools=[SerperDevTool(), ParallelSearchTool()],
            verbose=True,
            memory=False
        )

    @agent
    def report_compiler(self) -> Agent:
        return Agent(
            config=self.agents_config['report_compiler'],
            llm=claude_base,
            verbose=True,
            memory=False
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['company_research_task'],
            agent=self.company_researcher(),
            output_pydantic=CompanyResearchData
        )

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation_task'],
            agent=self.report_compiler(),
            context=[self.research_task()],
            output_pydantic=CompanyResearchReport
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
