"""
Examples of using Project Discovery to find and explore projects.

This solves the pain point: "What was that project path again?"
"""

import os
from gitlabmanager import GitLabClient

def example_list_all_projects(client: GitLabClient):
    """List all projects you have access to."""

    print("All your projects:")
    print("=" * 60)
    
    projects = client.packages.discover.list_all()
    
    for project in projects:
        print(f"\n{project['path_with_namespace']}")
        print(f"  ID: {project['id']}")
        print(f"  Description: {project['description'] or 'No description'}")
        print(f"  URL: {project['web_url']}")
        print(f"  Last activity: {project['last_activity_at']}")

def example_search_projects(client: GitLabClient):
    """Search for projects by name."""

    search_term = 'manager'
    
    print(f"Searching for projects with '{search_term}'...")
    print("=" * 60)
    
    results = client.packages.discover.search(query=search_term)
    
    print(f"\nFound {len(results)} projects:")
    for project in results:
        print(f"  - {project['path_with_namespace']}")

def example_find_by_namespace(client: GitLabClient):
    """Find all projects in a specific group/namespace."""

    namespace = 'tutorialprojects1'
    
    print(f"Projects in namespace '{namespace}':")
    print("=" * 60)
    
    projects = client.packages.discover.by_namespace(namespace)
    
    for project in projects:
        print(f"  - {project['name']}")
        print(f"    Path: {project['path_with_namespace']}")
        print(f"    Stars: {project['star_count']}")
        print()

def example_recent_activity(client: GitLabClient):
    """Show projects with recent activity."""

    print("Recently active projects (last 10):")
    print("=" * 60)
    
    recent = client.packages.discover.recent_activity(limit=10)
    
    for i, project in enumerate(recent, 1):
        print(f"\n{i}. {project['path_with_namespace']}")
        print(f"   Last activity: {project['last_activity_at']}")
        print(f"   URL: {project['web_url']}")

def example_get_project_details(client: GitLabClient):
    """Get detailed information about a specific project."""
    
    # You can use either project ID or path
    project_path = 'tutorialprojects1/softwareprojects/gitlab-manager'
    
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

def example_list_starred_projects(client: GitLabClient):
    """List your starred projects."""
    
    print("Your starred projects:")
    print("=" * 60)
    
    starred = client.packages.discover.list_all(starred=True)
    
    for project in starred:
        print(f"  - {project['path_with_namespace']}")
        print(f"    {project['description'] or 'No description'}")
        print()

def example_find_projects_with_packages(client: GitLabClient):
    """Find projects that have packages uploaded."""
    
    print("Projects with packages:")
    print("=" * 60)
    
    projects = client.packages.discover.list_with_packages(min_packages=1)
    
    for project in projects:
        print(f"  - {project['path_with_namespace']}")
        print(f"    Packages: {project['package_count']}")

def example_interactive_project_selector(client: GitLabClient):
    """Interactive project selector - super useful!"""
    
    print("=" * 60)
    print("=== Interactive Project Selector ===\n")
    
    # Search for projects
    search = input("Search for project (or press Enter for all): ").strip()
    
    if search:
        projects = client.packages.discover.search(search)
    else:
        projects = client.packages.discover.list_all()
    
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
            
            print(f"\nSelected: {selected['path_with_namespace']}")
            print(f"  ID: {selected['id']}")
            print(f"  URL: {selected['web_url']}")
            
            # Now you can use this project
            return selected['path_with_namespace']
        else:
            print("Invalid selection!")
    except ValueError:
        print("Invalid input!")

def example_organize_by_namespace(client: GitLabClient):
    """Organize projects by namespace/group."""
    
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

def main():
    
    print("=" * 60)
    print("GitLab Project Discovery Examples")
    print("=" * 60)

    # Initialize the client
    client = GitLabClient(
        url='https://gitlab.com',
        private_token=os.environ['GITLAB_TOKEN']
    )
    
    # Uncomment the example you want to run
    
    # Basic discovery
    print("\nExample: List all projects...")
    example_list_all_projects(client)
    print("\nExample: Search projects by name...")
    example_search_projects(client)
    print("\nExample: Find projects by namespace...")
    example_find_by_namespace(client)
    print("\nExample: Show recent activity...")
    example_recent_activity(client)
    print("\nExample: Get project details...")
    example_get_project_details(client)
    
    # Filtering
    print("\nExample: List starred projects...")
    example_list_starred_projects(client)
    print("\nExample: Find projects with packages...")
    example_find_projects_with_packages(client)
    
    # Advanced workflows
    print("\nExample: Interactive project selector...")
    example_interactive_project_selector(client)
    print("\nExample: Organize projects by namespace...")
    example_organize_by_namespace(client)

if __name__ == '__main__':
    main()
