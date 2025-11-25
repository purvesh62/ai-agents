import os
import agentops
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ParallelSearchTool, SerperDevTool
from crewai import LLM

from crew_agent.output_models import (
    CrewOutputSummary,
    InterviewPreparationTips,
    JobProfiler,
    JobCandidateProfile
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
class JobScreenerCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def job_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['job_analyst'],
            llm=claude_base,
            tools=[SerperDevTool()],
            verbose=True,
            memory=False
        )

    @agent
    def candidate_screener(self) -> Agent:
        return Agent(
            config=self.agents_config['candidate_screener'],
            llm=claude_base,
            tools=[ParallelSearchTool()],
            verbose=True,
            memory=False
        )

    @agent
    def interview_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['interview_coordinator'],
            llm=claude_base,
            verbose=True,
            memory=False
        )

    @agent
    def hiring_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['hiring_manager'],
            llm=claude_base,
            verbose=True,
            memory=False
        )

    @task
    def job_profile_task(self) -> Task:
        return Task(
            config=self.tasks_config['job_profiler_task'],
            agent=self.job_analyst(),
            output_pydantic=JobProfiler
        )

    @task
    def job_screening_task(self) -> Task:
        return Task(
            config=self.tasks_config['job_screening_task'],
            agent=self.candidate_screener(),
            context=[self.job_profile_task()],
            output_pydantic=JobCandidateProfile
        )

    @task
    def interview_prep_task(self) -> Task:
        return Task(
            config=self.tasks_config['job_interview_prep_task'],
            agent=self.interview_coordinator(),
            context=[self.job_screening_task()],
            output_pydantic=InterviewPreparationTips
        )

    @task
    def final_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_summary_task'],
            agent=self.hiring_manager(),
            context=[self.job_screening_task(), self.interview_prep_task()],
            output_pydantic=CrewOutputSummary
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
