from pydantic import BaseModel, Field
from typing import List


class JobProfiler(BaseModel):
    """Analysis of job screening results"""
    job_title: str = Field(description="Title of the job position")
    key_responsibilities: List[str] = Field(description="List of key responsibilities for the job")
    preferred_skills: List[str] = Field(description="List of preferred skills for the job")
    preferred_experience: str = Field(description="Preferred experience level for the job")
    company_overview: str = Field(description="Brief overview of the hiring company")
    ideal_candidate_profile: str = Field(description="Ideal profile of the candidate.")


class JobCandidateProfile(BaseModel):
    """Profile of a job candidate"""
    name: str = Field(description="Full name of the candidate")
    skills: List[str] = Field(description="List of skills possessed by the candidate")
    experience_years: int = Field(description="Number of years of relevant experience")
    education: str = Field(description="Highest level of education attained")
    certifications: List[str] = Field(description="Relevant certifications held by the candidate")
    strengths: List[str] = Field(description="List of strengths identified during screening")
    weaknesses: List[str] = Field(description="List of weaknesses identified during screening")
    overall_fit: str = Field(description="Overall fit assessment for the role")
    suggested_next_steps: List[str] = Field(description="Suggested next steps in the hiring process")


class InterviewPreparationTips(BaseModel):
    """Tips for interview preparation"""
    common_questions: List[str] = Field(description="List of common interview questions")
    best_practices: List[str] = Field(description="Best practices for interview preparation")
    resources: List[str] = Field(description="Recommended resources for further study")


class CrewOutputSummary(BaseModel):
    """Summary of the crew's overall output"""
    summary: str = Field(description="A brief summary of the main points")
    key_points: List[str] = Field(description="List of key points discussed")
    recommendations: List[str] = Field(description="Actionable recommendations based on the analysis")
    name: str = Field(description="Full name of the candidate")
    skills: List[str] = Field(description="List of skills possessed by the candidate")
    experience_years: int = Field(description="Number of years of relevant experience")
    education: str = Field(description="Highest level of education attained")
    certifications: List[str] = Field(description="Relevant certifications held by the candidate")
    strengths: List[str] = Field(description="List of strengths identified during screening")
    weaknesses: List[str] = Field(description="List of weaknesses identified during screening")
    overall_fit: str = Field(description="Overall fit assessment for the role")
    suggested_next_steps: List[str] = Field(description="Suggested next steps in the hiring process")
    common_questions: List[str] = Field(description="List of common interview questions")
    best_practices: List[str] = Field(description="Best practices for interview preparation")
    resources: List[str] = Field(description="Recommended resources for further study")
