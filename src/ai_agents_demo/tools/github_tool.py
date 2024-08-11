from crewai_tools import tool
import requests
from dotenv import load_dotenv
import os
import base64
import json

load_dotenv()

GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')

def github_api_request(url, method='GET', data=None):
    headers = {
        'Authorization': f'token {GITHUB_API_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method == 'PATCH':
        response = requests.patch(url, headers=headers, json=data)
    else:
        raise ValueError("Unsupported HTTP method")
    
    if response.status_code in (200, 201):
        return response.json()
    else:
        raise Exception(f"GitHub API request failed: {response.status_code} {response.text}")

@tool
def fetch_github_repo(repo_url: str) -> str:
    """
    Fetch the contents of the specified GitHub repository.
    """
    owner_repo = repo_url.split('github.com/')[-1]
    repo_api_url = f"https://api.github.com/repos/{owner_repo}/contents"
    repo_contents = github_api_request(repo_api_url)
    formatted_contents = {item['path']: item for item in repo_contents}
    return json.dumps(formatted_contents, indent=2)

@tool
def commit_changes_to_github(repo_url: str, changes: dict, commit_message: str) -> str:
    """
    Commit changes to the specified GitHub repository.
    """
    owner_repo = repo_url.split('github.com/')[-1]
    repo_api_url = f"https://api.github.com/repos/{owner_repo}"

    # Fetch the reference of the main branch
    ref = github_api_request(f"{repo_api_url}/git/refs/heads/main")
    sha_latest_commit = ref['object']['sha']

    # Fetch the commit object
    commit = github_api_request(f"{repo_api_url}/git/commits/{sha_latest_commit}")

    # Create blobs for each file change
    blobs = []
    for path, content in changes.items():
        blob = github_api_request(f"{repo_api_url}/git/blobs", method='POST', data={
            'content': content,
            'encoding': 'utf-8'
        })
        blobs.append({
            'path': path,
            'mode': '100644',
            'type': 'blob',
            'sha': blob['sha']
        })

    # Create a new tree
    new_tree = github_api_request(f"{repo_api_url}/git/trees", method='POST', data={
        'base_tree': commit['tree']['sha'],
        'tree': blobs
    })

    # Create a new commit
    new_commit = github_api_request(f"{repo_api_url}/git/commits", method='POST', data={
        'message': commit_message,
        'tree': new_tree['sha'],
        'parents': [sha_latest_commit]
    })

    # Update the reference to point to the new commit
    github_api_request(f"{repo_api_url}/git/refs/heads/main", method='PATCH', data={
        'sha': new_commit['sha']
    })

    return "Changes committed successfully."
