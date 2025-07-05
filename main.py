import logging
import os
import json
import time
from token.py import token       #Local!!!!!

import requests

#Logging configuration

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

broken_repos = []


def getRepos(language = "csharp"):
    return None


def readRepoList():
    path = os.getcwd()
    print(f"Current working directory: {path}")
    json_repositories = None
    for (dirpath, dirnames, filenames) in os.walk(path):
        print(f"Directory: {dirpath}")
        print(f"Subdirectories: {dirnames}")
        print(f"Files: {filenames}")
        print("===================================")
        
        if "popular_repos.json" in filenames:
            with open(os.path.join(dirpath, "popular_repos.json"),"r", encoding="utf8") as json_data:
                json_repositories = json.load(json_data)
                json_data.close()

    if json_repositories is None:
        print("No repositories.txt file found in the current directory or its subdirectories.")
        return None
    print("Repositories loaded successfully.")
    
    print(len(json_repositories))
    
    
    
def getListOfRepos():
    with open("popular_repos.json", "r", encoding="utf8") as json_data:
        json_repositories = json.load(json_data)
        json_data.close()
        with open("repos.txt", "w", encoding="utf8") as text_file:
            for repo in json_repositories:
                text_file.write(repo["html_url"] + "\n")
    
    
def beautifyJson():
    with open("popular_repos.json", "r", encoding="utf8") as json_data:
        data = json.load(json_data)
        json_data.close()
        new_Repos = []
        for repo in data:
            commits_url = repo.get("commits_url", "").replace("{/sha}", "")
            try:
                total_commits = get_all_commits_count(commits_url)
            except Exception as e:
                logging.error(f"Error fetching commits for {repo.get('name')}: {e}")
                
                total_commits = 0
            print(f"Total commits for {repo.get('name')}: {total_commits}")
            
            filtered_repo= {
                "name": repo.get("name"),
                "clone_url": repo.get("clone_url"),
                "html_url": repo.get("html_url"),
                "stargazers_count": repo.get("stargazers_count"),
                "size": repo.get("size"),
                "commits_url": repo.get("commits_url", "").replace("{/sha}", ""),
                "total_commits": total_commits
            }
            new_Repos.append(filtered_repo)
        print(f"Filtered repositories: {len(new_Repos)}")
        with open("beautified_repos.json", "w", encoding="utf8") as json_data:
            json.dump(new_Repos, json_data, indent=2)
            json_data.close()    
GITHUB_TOKEN = "token"  # Replace with your token string for better rate limits

def get_all_commits_count(commits_url):
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    per_page = 100  # Max GitHub allows
    page = 1
    total_commits = 0

    while True:
        try:
            response = requests.get(
            commits_url,
            headers=headers,
            params={"per_page": per_page, "page": page},
            timeout=15  # Set a timeout for the request
        )
        except(requests.Timeout, ConnectionError) as e:
            logging.error(f"Error fetching commits(last count {total_commits}) from {commits_url}: {e}")
            time.sleep(30)
            return total_commits
        except requests.HTTPError as e:
            logging.error(f"HTTP error fetching commits(last count {total_commits}) from {commits_url}: {e}")
            return total_commits
        # Check for rate limiting
        if response.status_code != 200:
            logging.error(f"Failed to get commits from {commits_url} (status {response.status_code})")
            time.sleep(20)
            return total_commits

        commits = response.json()
        if not isinstance(commits, list):
            print(f"Unexpected response structure at page {page}: {commits}")
            return total_commits

        commit_count = len(commits)
        total_commits += commit_count
        logging.info(f"Received {commit_count} commits from {commits_url} (page {page})")
        if commit_count < per_page:
            break  # Last page reached

        page += 1
        time.sleep(0.1)  # Avoid rate limits (especially without token)

    return total_commits
#readRepoList()
#getListOfRepos()

beautifyJson()