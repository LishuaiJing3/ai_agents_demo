from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.github_tool import fetch_github_repo, commit_changes_to_github

@CrewBase
class GithubInteractorCrew:
    """GithubInteractor crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def code_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['code_analyzer'],
            tools=[fetch_github_repo],
            verbose=True
        )

    @agent
    def code_improver(self) -> Agent:
        return Agent(
            config=self.agents_config['code_improver'],
            tools=[commit_changes_to_github],
            verbose=True
        )

    @agent
    def query_responder(self) -> Agent:
        return Agent(
            config=self.agents_config['query_responder'],
            tools=[fetch_github_repo],
            verbose=True
        )

    @task
    def analyze_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_code_task'],
            agent=self.code_analyzer()
        )

    @task
    def improve_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['improve_code_task'],
            agent=self.code_improver()
        )

    @task
    def respond_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['respond_query_task'],
            agent=self.query_responder()
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GithubInteractor crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=2
        )
