import os
from crew_agent.company_research_crew import CompanyResearchCrew


def write_markdown_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)


def run_crew(company_name: str):
    """
    Run company research crew for a given company name.

    Args:
        company_name: Name of the company to research
    """
    input_data = {
        "company_name": company_name
    }

    print(f"\n{'=' * 60}")
    print(f"🔍 Starting research for: {company_name}")
    print(f"{'=' * 60}\n")

    crew = CompanyResearchCrew().crew()
    result = crew.kickoff(inputs=input_data)

    # Get the markdown report from the result
    markdown_report = result.pydantic.markdown_report

    # Save the markdown report
    file_name = f'output/{company_name.replace(" ", "_").lower()}_report.md'
    os.makedirs('output', exist_ok=True)
    write_markdown_file(markdown_report, file_name)

    print(f"\n{'=' * 60}")
    print(f"✅ Research Complete!")
    print(f"📄 Report saved to: {file_name}")
    print(f"{'=' * 60}")
    print("\n📊 Usage Statistics:")
    print(result.token_usage)
    print(f"{'=' * 60}\n")

    return markdown_report


if __name__ == "__main__":
    # Example usage - replace with your company name
    # company_name = input("Enter company name to research: ").strip()
    company_name = "HubSpot hubspot.com" # For testing purposes
    if company_name:
        run_crew(company_name)
    else:
        print("Please provide a company name!")
