from pydantic import BaseModel, Field
from typing import List, Optional


class CompanyResearchData(BaseModel):
    """Comprehensive company research data"""
    company_name: str = Field(description="Official name of the company")
    tagline: str = Field(description="Company tagline or slogan")
    website: str = Field(description="Company website URL")
    industry: str = Field(description="Primary industry the company operates in")
    employee_count: str = Field(description="Approximate number of employees")
    founded_year: str = Field(description="Year the company was founded")
    company_type: str = Field(description="Type of company (e.g., Public, Private, Startup)")
    revenue: Optional[str] = Field(default="Not available", description="Company revenue information if available")
    latest_news: List[str] = Field(description="Recent news articles or updates about the company")
    product_summary: str = Field(description="Summary of main products or services offered")
    competitors: List[str] = Field(description="List of main competitors")
    technology_stack: List[str] = Field(description="Technologies and tools used by the company")
    hiring_status: str = Field(description="Current hiring status in Canada")
    tech_job_roles: List[str] = Field(description="Available tech job roles in Canada")
    financial_info: str = Field(description="Financial information including funding rounds, valuation, etc.")
    key_people: List[str] = Field(description="Key executives and leadership team members")
    funding_acquisitions: str = Field(description="Funding rounds and acquisition history")
    domains: List[str] = Field(description="Related domains and web properties")


class CompanyResearchReport(BaseModel):
    """Final markdown formatted company research report"""
    markdown_report: str = Field(description="Complete company research report in markdown format")
