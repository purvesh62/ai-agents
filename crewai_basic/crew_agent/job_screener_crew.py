import os
import agentops
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ParallelSearchTool
from crewai import LLM

from crew_agent.output_models import CrewOutputSummary, InterviewPreparationTips

openai = LLM(model='openai/gpt-5-mini-2025-08-07', api_key=os.getenv('OPENAI_API_KEY'))
claude = LLM(model='claude-sonnet-4-5-20250929', api_key=os.getenv('ANTHROPIC_API_KEY'))

agentops.init()


@CrewBase
class JobScreenerCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def job_recruiter(self) -> Agent:
        return Agent(
            config=self.agents_config['job_recruiter'],
            llm=openai,
            tools=[ParallelSearchTool()],
            verbose=True,
            memory=False
        )

    @task
    def job_profile_task(self) -> Task:
        return Task(
            config=self.tasks_config['job_profiler_task'],
            agent=self.job_recruiter(),
            tools=[ParallelSearchTool()],
        )

    @task
    def job_screening_task(self) -> Task:
        return Task(
            config=self.tasks_config['job_screening_task'],
            agent=self.job_recruiter(),
            tools=[ParallelSearchTool()],
            context=[self.job_profile_task()],
        )

    @task
    def interview_prep_task(self) -> Task:
        return Task(
            config=self.tasks_config['job_interview_prep_task'],
            agent=self.job_recruiter(),
            context=[self.job_screening_task()],
            output_pydantic=InterviewPreparationTips
        )

    @task
    def final_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_summary_task'],
            agent=self.job_recruiter(),
            context=[self.job_profile_task(), self.job_screening_task(), self.interview_prep_task()],
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
