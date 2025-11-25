import json
import uuid
from crewai_basic.crew_agent.job_screener_crew import JobScreenerCrew


def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def write_json_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def run_crew():
    job_title = "Software Engineer"
    company_website = "https://www.example.com"
    job_description = read_file('input/job_description.txt')
    resume = read_file('input/candidate_resume.txt')

    input_data = {
        "job_title": job_title,
        "job_description": job_description,
        "company_website": company_website,
        "candidate_resume": resume
    }
    

    crew = JobScreenerCrew().crew()
    result = crew.kickoff(inputs=input_data)
    result_dict = result.model_dump()
    write_json_file(json.loads(result_dict.get('raw')), f'output_{str(uuid.uuid4())}.json')
    print("\n" + "=" * 60)
    print("🧠 Research Crew Result")
    print("=" * 60)
    print(result)
    pass

if __name__ == "__main__":
    run_crew()
