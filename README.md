# GitLab Manager

Enhanced GitLab operations and automation library - a powerful Python wrapper around python-gitlab.

## Features

- **Package Management**: Upload, download, list, and manage GitLab packages
- **Release Management**: Create and manage releases with assets
- **CI/CD Operations**: Trigger and monitor pipelines
- **Repository Operations**: Manage branches, tags, and repository content
- **Simplified API**: High-level, intuitive operations for common workflows
- **Better Error Handling**: Clear exceptions and error messages

## Installation

```bash
pip install gitlab-manager
```

## Quick Start

```python
from gitlabmanager import GitLabClient

# Initialize the client
client = GitLabClient(
    url='https://gitlab.com',
    private_token='your-token-here'
)

# Upload a package
client.packages.upload(
    project_id='mygroup/myproject',
    file_path='dist/package-1.0.tar.gz'
)

# Create a release
client.releases.create(
    project_id='mygroup/myproject',
    tag_name='v1.0.0',
    name='Version 1.0.0',
    description='First stable release'
)

# Trigger a pipeline
pipeline = client.pipelines.trigger(
    project_id='mygroup/myproject',
    ref='main',
    variables={'DEPLOY': 'production'}
)
```

## Authentication

You can authenticate using:

1. **Personal Access Token** (recommended):
```python
client = GitLabClient(
    url='https://gitlab.com',
    private_token='your-token'
)
```

2. **OAuth Token**:
```python
client = GitLabClient(
    url='https://gitlab.com',
    oauth_token='your-oauth-token'
)
```

3. **CI Job Token** (for use in GitLab CI):
```python
import os
client = GitLabClient(
    url='https://gitlab.com',
    job_token=os.environ['CI_JOB_TOKEN']
)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/gitlab-manager.git
cd gitlab-manager

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
black --check src/

# Type checking
mypy src/
```

## Requirements

- Python >= 3.8
- python-gitlab >= 4.0.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Status

🚧 **Currently in early development (v0.1.0)** - API may change

Core features under development:
- [ ] Package operations
- [ ] Release management
- [ ] Pipeline operations
- [ ] Repository management
- [ ] Documentation
- [ ] Test coverage