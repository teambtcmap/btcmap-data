import os
import requests
from github import Github
from datetime import datetime

# Configuration
GH_TOKEN = os.getenv('GITHUB_TOKEN')
GITEA_URL = os.getenv('GITEA_URL')  # e.g., "https://your-gitea.com"
GITEA_TOKEN = os.getenv('GITEA_TOKEN')
REPO_OWNER = "your-github-org"
GITHUB_REPO = "source-repo"
GITEA_REPO_OWNER = "your-gitea-org"
GITEA_REPO = "target-repo"

# GitHub API client
gh = Github(GH_TOKEN)
repo = gh.get_repo(f"{REPO_OWNER}/{GITHUB_REPO}")

# Gitea headers
gitea_headers = {
		"Authorization": f"token {GITEA_TOKEN}",
		"Content-Type": "application/json"
}

def create_gitea_issue(issue, labels=None):
		"""Create an issue in Gitea and return its number"""
		url = f"{GITEA_URL}/api/v1/repos/{GITEA_REPO_OWNER}/{GITEA_REPO}/issues"
		data = {
				"title": issue.title,
				"body": format_body(issue),
				"closed": issue.state == "closed",
				"labels": labels or [],
				"created_at": issue.created_at.isoformat()
		}

		response = requests.post(url, json=data, headers=gitea_headers)
		if response.status_code != 201:
				raise Exception(f"Failed to create issue: {response.text}")

		return response.json()["number"]

def migrate_comments(github_issue, gitea_issue_number):
		"""Migrate comments from GitHub issue to Gitea"""
		url = f"{GITEA_URL}/api/v1/repos/{GITEA_REPO_OWNER}/{GITEA_REPO}/issues/{gitea_issue_number}/comments"

		for comment in github_issue.get_comments():
				data = {
						"body": format_comment(comment),
						"created_at": comment.created_at.isoformat()
				}
				requests.post(url, json=data, headers=gitea_headers)

def format_body(issue):
		"""Format GitHub issue body with original metadata"""
		return f"""**Original GitHub Issue**: [{issue.number}]({issue.html_url})
*Created by @{issue.user.login} on {issue.created_at.strftime('%Y-%m-%d %H:%M')}*

{issue.body}"""

def format_comment(comment):
		"""Format GitHub comment with original metadata"""
		return f"""**Comment from @{comment.user.login}** ({comment.created_at.strftime('%Y-%m-%d %H:%M')}):

{comment.body}"""

def sync_labels():
		"""Sync GitHub labels to Gitea repository"""
		# Get existing Gitea labels
		labels_url = f"{GITEA_URL}/api/v1/repos/{GITEA_REPO_OWNER}/{GITEA_REPO}/labels"
		existing_labels = {l["name"]: l["id"] for l in requests.get(labels_url, headers=gitea_headers).json()}

		# Create missing labels
		for gh_label in repo.get_labels():
				if gh_label.name not in existing_labels:
						data = {
								"name": gh_label.name,
								"color": gh_label.color.lstrip("#"),
								"description": gh_label.description or ""
						}
						requests.post(labels_url, json=data, headers=gitea_headers)

def main():
		print("Syncing labels...")
		sync_labels()

		print("Migrating issues...")
		for issue in repo.get_issues(state="all"):
				if issue.pull_request:  # Skip pull requests
						continue

				print(f"Processing issue #{issue.number}: {issue.title}")

				# Get label IDs
				labels = [l.name for l in issue.labels]

				# Create issue in Gitea
				gitea_number = create_gitea_issue(issue, labels)

				# Migrate comments
				migrate_comments(issue, gitea_number)

				# Close if needed
				if issue.state == "closed":
						close_url = f"{GITEA_URL}/api/v1/repos/{GITEA_REPO_OWNER}/{GITEA_REPO}/issues/{gitea_number}"
						requests.patch(close_url, json={"state": "closed"}, headers=gitea_headers)

if __name__ == "__main__":
		main()
