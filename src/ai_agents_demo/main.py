from .crew import GithubInteractorCrew

if __name__ == "__main__":
    crew_instance = GithubInteractorCrew()
    repo_url = 'https://github.com/LishuaiJing3/data-science-project-template.git'
    result = crew_instance.crew().kickoff(inputs={'repo_url': repo_url})
    print(result)
