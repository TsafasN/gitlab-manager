import gitlab
import os


class GitLabClient:
    """Enhanced GitLab operations and automation library."""

    def __init__(self, url, token):
        self._gl = gitlab.Gitlab(url, private_token=token)
        # gl = gitlab.Gitlab('https://gitlab.com', private_token=os.environ['GITLAB_TOKEN'])

        # What can we do?
        print(dir(self._gl))  # See all available methods/attributes

        # Try getting a project
        project = self._gl.projects.get("52929099")  # Use one of your project IDs
        print(type(project))
        print(dir(project))  # What can we do with a project?
