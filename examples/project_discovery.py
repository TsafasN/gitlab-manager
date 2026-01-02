"""
Examples of using Project Discovery to find and explore projects.

This solves the pain point: "What was that project path again?"
"""

import os
from gitlabmanager import GitLabClient


def example_list_all_projects():
    """List all projects you have access to."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("All your projects:")
    print("=" * 60)
    
    projects = client.packages.discover.list_all()
    
    for project in projects:
        print(f"\n{project['path_with_namespace']}")
        print(f"  ID: {project['id']}")
        print(f"  Description: {project['description'] or 'No description'}")
        print(f"  URL: {project['web_url']}")
        print(f"  Last activity: {project['last_activity_at']}")


def example_search_projects():
    """Search for projects by name."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    search_term = 'docker'
    
    print(f"Searching for projects with '{search_term}'...")
    print("=" * 60)
    
    results = client.packages.discover.search(search_term)
    
    print(f"\nFound {len(results)} projects:")
    for project in results:
        print(f"  - {project['path_with_namespace']}")


def example_find_by_namespace():
    """Find all projects in a specific group/namespace."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    namespace = 'mygroup'
    
    print(f"Projects in namespace '{namespace}':")
    print("=" * 60)
    
    projects = client.packages.discover.by_namespace(namespace)
    
    for project in projects:
        print(f"  - {project['name']}")
        print(f"    Path: {project['path_with_namespace']}")
        print(f"    Stars: {project['star_count']}")
        print()


def example_recent_activity():
    """Show projects with recent activity."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("Recently active projects (last 10):")
    print("=" * 60)
    
    recent = client.packages.discover.recent_activity(limit=10)
    
    for i, project in enumerate(recent, 1):
        print(f"\n{i}. {project['path_with_namespace']}")
        print(f"   Last activity: {project['last_activity_at']}")
        print(f"   URL: {project['web_url']}")


def example_get_project_details():
    """Get detailed information about a specific project."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    # You can use either project ID or path
    project_path = 'mygroup/myproject'
    
    print(f"Project details for: {project_path}")
    print("=" * 60)
    
    info = client.packages.discover.get_project_info(project_path)
    
    print(f"\nBasic Info:")
    print(f"  ID: {info['id']}")
    print(f"  Name: {info['name']}")
    print(f"  Description: {info['description']}")
    print(f"  Visibility: {info['visibility']}")
    print(f"  Created: {info['created_at']}")
    
    print(f"\nRepository URLs:")
    print(f"  HTTPS: {info['http_url_to_repo']}")
    print(f"  SSH: {info['ssh_url_to_repo']}")
    
    print(f"\nStatistics:")
    print(f"  Stars: {info['star_count']}")
    print(f"  Forks: {info['forks_count']}")
    
    if info.get('topics'):
        print(f"  Topics: {', '.join(info['topics'])}")


def example_list_owned_projects():
    """List only projects you own."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("Projects you own:")
    print("=" * 60)
    
    my_projects = client.packages.discover.list_all(owned=True)
    
    for project in my_projects:
        print(f"  - {project['path_with_namespace']}")


def example_list_starred_projects():
    """List your starred projects."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("Your starred projects:")
    print("=" * 60)
    
    starred = client.packages.discover.list_all(starred=True)
    
    for project in starred:
        print(f"  - {project['path_with_namespace']}")
        print(f"    {project['description'] or 'No description'}")
        print()


def example_find_projects_with_packages():
    """Find projects that have packages uploaded."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("Projects with packages:")
    print("=" * 60)
    
    projects = client.packages.discover.list_with_packages(min_packages=1)
    
    for project in projects:
        print(f"  - {project['path_with_namespace']}")
        print(f"    Packages: {project['package_count']}")


def example_interactive_project_selector():
    """Interactive project selector - super useful!"""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("=== Interactive Project Selector ===\n")
    
    # Search for projects
    search = input("Search for project (or press Enter for all): ").strip()
    
    if search:
        projects = client.packages.discover.search(search)
    else:
        projects = client.packages.discover.list_all(owned=True)
    
    if not projects:
        print("No projects found!")
        return
    
    # Display projects
    print(f"\nFound {len(projects)} projects:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project['path_with_namespace']}")
    
    # Select project
    try:
        choice = int(input("\nSelect project number: "))
        if 1 <= choice <= len(projects):
            selected = projects[choice - 1]
            
            print(f"\n✓ Selected: {selected['path_with_namespace']}")
            print(f"  ID: {selected['id']}")
            print(f"  URL: {selected['web_url']}")
            
            # Now you can use this project
            return selected['path_with_namespace']
        else:
            print("Invalid selection!")
    except ValueError:
        print("Invalid input!")


def example_save_project_shortcuts():
    """Save frequently used projects to a local file."""
    import json
    
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    # Get your favorite projects
    favorites = client.packages.discover.list_all(starred=True)
    
    # Save to file
    shortcuts = {}
    for project in favorites:
        # Create short aliases
        short_name = project['path'].lower()
        shortcuts[short_name] = {
            'id': project['id'],
            'path': project['path_with_namespace'],
            'url': project['web_url'],
        }
    
    with open('gitlab_shortcuts.json', 'w') as f:
        json.dump(shortcuts, f, indent=2)
    
    print("✓ Saved shortcuts to gitlab_shortcuts.json")
    print("\nYour shortcuts:")
    for name, info in shortcuts.items():
        print(f"  {name} → {info['path']}")


def example_use_shortcuts():
    """Use saved shortcuts."""
    import json
    
    # Load shortcuts
    with open('gitlab_shortcuts.json', 'r') as f:
        shortcuts = json.load(f)
    
    # Use shortcut
    short_name = 'myapp'  # Instead of 'mygroup/myapp/backend'
    
    if short_name in shortcuts:
        project_info = shortcuts[short_name]
        print(f"Using project: {project_info['path']}")
        
        # Now upload to it
        client = GitLabClient(
            url='https://gitlab.com',
            private_token=os.environ['GITLAB_TOKEN']
        )
        
        result = client.packages.upload(
            project_id=project_info['path'],  # Full path from shortcut
            file_path='package.tar.gz',
            package_version='1.0.0',
        )
        
        print(f"✓ Uploaded to {project_info['path']}")


def example_organize_by_namespace():
    """Organize projects by namespace/group."""
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    print("Projects organized by namespace:")
    print("=" * 60)
    
    # Get all projects
    all_projects = client.packages.discover.list_all()
    
    # Organize by namespace
    by_namespace = {}
    for project in all_projects:
        namespace = project['namespace'].get('path', 'unknown')
        if namespace not in by_namespace:
            by_namespace[namespace] = []
        by_namespace[namespace].append(project)
    
    # Display organized
    for namespace, projects in sorted(by_namespace.items()):
        print(f"\n{namespace}/ ({len(projects)} projects)")
        for project in projects:
            print(f"  └─ {project['path']}")


if __name__ == '__main__':
    # Uncomment the example you want to run
    
    # Basic discovery
    example_list_all_projects()
    # example_search_projects()
    # example_find_by_namespace()
    # example_recent_activity()
    # example_get_project_details()
    
    # Filtering
    # example_list_owned_projects()
    # example_list_starred_projects()
    # example_find_projects_with_packages()
    
    # Advanced workflows
    # example_interactive_project_selector()
    # example_save_project_shortcuts()
    # example_use_shortcuts()
    # example_organize_by_namespace()
    
    pass