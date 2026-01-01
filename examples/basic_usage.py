"""Basic usage example for GitLab Manager."""

from gitlabmanager import GitLabClient
import os

# Initialize client with token from environment
client = GitLabClient(
    url='https://gitlab.com',
    private_token=os.environ.get('GITLAB_TOKEN')
)

# Get a project
project = client.get_project('52929099')
print(f"Project: {project.name}")
print(f"Description: {project.description}")

# Access the underlying python-gitlab client if needed
# for operations not yet wrapped
gl = client.gitlab
user = gl.user
print(f"Authenticated as: {user.username}")