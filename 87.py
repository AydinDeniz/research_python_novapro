# Prompt 87

import requests
import csv
from github import Github

# Initialize GitHub API client
g = Github("your_github_token")

# Function to collect repository data
def collect_repo_data(org_name):
    org = g.get_organization(org_name)
    repos = org.get_repos()
    data = []
    
    for repo in repos:
        repo_data = {
            "name": repo.name,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "issues": repo.get_issues().totalCount,
            "commits": len(list(repo.get_commits()))
        }
        data.append(repo_data)
    
    return data

# Function to analyze contributor activity
def analyze_contributor_activity(org_name):
    org = g.get_organization(org_name)
    repos = org.get_repos()
    contributors = {}
    
    for repo in repos:
        for contributor in repo.get_contributors():
            if contributor.login not in contributors:
                contributors[contributor.login] = 0
            contributors[contributor.login] += contributor.contributions
    
    return contributors

# Function to produce CSV summary report
def produce_csv_report(repo_data, contributor_activity, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Repository", "Stars", "Forks", "Issues", "Commits"])
        
        for data in repo_data:
            writer.writerow([data["name"], data["stars"], data["forks"], data["issues"], data["commits"]])
        
        writer.writerow([])
        writer.writerow(["Contributor", "Contributions"])
        
        for contributor, contributions in contributor_activity.items():
            writer.writerow([contributor, contributions])

# Main function
def main():
    org_name = "your_organization_name"
    repo_data = collect_repo_data(org_name)
    contributor_activity = analyze_contributor_activity(org_name)
    produce_csv_report(repo_data, contributor_activity, "summary_report.csv")

if __name__ == "__main__":
    main()