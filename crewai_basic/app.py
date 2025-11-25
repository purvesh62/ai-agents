import json
import os
import uuid
from crew_agent.job_screener_crew import JobScreenerCrew


def read_file(filename):
    with open(f'{os.getcwd()}/{filename}', 'r') as f:
        print(f"Reading file: {filename}")
        return f.read()


def write_json_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def run_crew():
    job_title = read_file('input/job_role.txt')
    company_website = read_file('input/company.txt')
    job_description = read_file('input/job_description.txt')
    resume = read_file('input/resume.txt')

    input_data = {
        "job_title": job_title,
        "job_description": job_description,
        "company_website": company_website,
        "candidate_resume": resume
    }

    crew = JobScreenerCrew().crew()
    result = crew.kickoff(inputs=input_data)
    pydantic_dict = result.pydantic.model_dump()
    file_name = f'output_{str(uuid.uuid4())}.json'
    write_json_file(pydantic_dict, file_name)
    print("\n" + "=" * 60)
    print(f"🧠 Research Crew Result: {file_name}")
    print("=" * 60)
    print("Usage Statistics:")
    print(result.token_usage)
    print("=" * 60)


if __name__ == "__main__":
    run_crew()
