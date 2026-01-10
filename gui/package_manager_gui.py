"""
GitLab Package Manager GUI with Project Discovery.

Enhanced GUI with visual project browser and search.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional, List, Dict, Any
import threading

from gitlabmanager import GitLabClient
from gitlabmanager.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    OperationError,
    AuthenticationError,
)


class PackageManagerGUI:
    """Main GUI application for GitLab Package Manager."""
    
    def __init__(self):
        """Initialize the GUI application."""
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("GitLab Package Manager")
        self.root.geometry("1200x750")
        
        # GitLab client (will be initialized after login)
        self.client: Optional[GitLabClient] = None
        self.current_project: Optional[str] = None
        self.discovered_projects: List[Dict[str, Any]] = []
        
        # Create UI
        self.create_login_screen()
        
    def create_login_screen(self):
        """Create the login/connection screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Center frame
        login_frame = ctk.CTkFrame(self.root)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            login_frame,
            text="GitLab Package Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20, padx=40)
        
        # URL input
        url_label = ctk.CTkLabel(login_frame, text="GitLab URL:")
        url_label.pack(pady=(10, 0))
        
        self.url_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="https://gitlab.com",
            width=300
        )
        self.url_entry.pack(pady=5)
        self.url_entry.insert(0, "https://gitlab.com")
        
        # Token input
        token_label = ctk.CTkLabel(login_frame, text="Personal Access Token:")
        token_label.pack(pady=(10, 0))
        
        self.token_entry = ctk.CTkEntry(
            login_frame,
            placeholder_text="Enter your token",
            width=300,
            show="*"
        )
        self.token_entry.pack(pady=5)
        
        # Load from env if available
        if 'GITLAB_TOKEN' in os.environ:
            self.token_entry.insert(0, os.environ['GITLAB_TOKEN'])
        
        # Connect button
        connect_btn = ctk.CTkButton(
            login_frame,
            text="Connect",
            command=self.connect_to_gitlab,
            width=200
        )
        connect_btn.pack(pady=20)
        
        # Status label
        self.login_status = ctk.CTkLabel(login_frame, text="", text_color="red")
        self.login_status.pack(pady=5)
        
    def connect_to_gitlab(self):
        """Connect to GitLab with provided credentials."""
        url = self.url_entry.get().strip()
        token = self.token_entry.get().strip()
        
        if not url or not token:
            self.login_status.configure(text="Please enter both URL and token")
            return
        
        self.login_status.configure(text="Connecting...", text_color="yellow")
        self.root.update()
        
        try:
            self.client = GitLabClient(url=url, private_token=token)
            self.create_main_screen()
        except AuthenticationError as e:
            self.login_status.configure(
                text=f"Authentication failed: {str(e)[:50]}",
                text_color="red"
            )
        except Exception as e:
            self.login_status.configure(
                text=f"Connection failed: {str(e)[:50]}",
                text_color="red"
            )
    
    def create_main_screen(self):
        """Create the main package management screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main layout with sidebar
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Show project browser by default
        self.show_project_browser()
    
    def create_sidebar(self):
        """Create the sidebar with navigation."""
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            sidebar,
            text="Package Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20)
        
        # Navigation buttons
        projects_btn = ctk.CTkButton(
            sidebar,
            text="🔍 Browse Projects",
            command=self.show_project_browser,
            width=160
        )
        projects_btn.grid(row=1, column=0, padx=20, pady=10)
        
        upload_btn = ctk.CTkButton(
            sidebar,
            text="📤 Upload",
            command=self.show_upload_view,
            width=160
        )
        upload_btn.grid(row=2, column=0, padx=20, pady=10)
        
        list_btn = ctk.CTkButton(
            sidebar,
            text="📋 List Packages",
            command=self.show_list_view,
            width=160
        )
        list_btn.grid(row=3, column=0, padx=20, pady=10)
        
        download_btn = ctk.CTkButton(
            sidebar,
            text="📥 Download",
            command=self.show_download_view,
            width=160
        )
        download_btn.grid(row=4, column=0, padx=20, pady=10)
        
        search_btn = ctk.CTkButton(
            sidebar,
            text="🔎 Search Packages",
            command=self.show_search_view,
            width=160
        )
        search_btn.grid(row=5, column=0, padx=20, pady=10)
        
        # Disconnect button at bottom
        disconnect_btn = ctk.CTkButton(
            sidebar,
            text="🔌 Disconnect",
            command=self.create_login_screen,
            width=160,
            fg_color="gray"
        )
        disconnect_btn.grid(row=8, column=0, padx=20, pady=20)
    
    def clear_main_frame(self):
        """Clear the main content area."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_project_browser(self):
        """Show the project discovery and browser interface."""
        self.clear_main_frame()
        
        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Browse Projects",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # Search input
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=10)
        
        self.project_search_entry = ctk.CTkEntry(search_frame, width=200)
        self.project_search_entry.pack(side="left", padx=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_projects,
            width=100
        )
        search_btn.pack(side="left", padx=5)
        
        # Filter options
        self.starred_only_var = ctk.BooleanVar(value=False)
        starred_check = ctk.CTkCheckBox(
            search_frame,
            text="Starred only",
            variable=self.starred_only_var,
            command=self.load_all_projects
        )
        starred_check.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.load_all_projects,
            width=100
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Projects display area (scrollable)
        self.projects_display = ctk.CTkScrollableFrame(self.main_frame)
        self.projects_display.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Load projects automatically
        self.load_all_projects()
    
    def load_all_projects(self):
        """Load and display all projects."""
        # Clear current display
        for widget in self.projects_display.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(
            self.projects_display,
            text="Loading projects..."
        )
        loading_label.pack(pady=20)
        
        def load_thread():
            try:
                starred = self.starred_only_var.get()
                projects = self.client.packages.discover.list_all(starred=starred)
                self.root.after(0, lambda: self.display_projects(projects))
            except Exception as e:
                self.root.after(0, lambda: self.show_projects_error(str(e)))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def search_projects(self):
        """Search for projects."""
        query = self.project_search_entry.get().strip()
        
        if not query:
            self.load_all_projects()
            return
        
        # Clear current display
        for widget in self.projects_display.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(
            self.projects_display,
            text=f"Searching for '{query}'..."
        )
        loading_label.pack(pady=20)
        
        def search_thread():
            try:
                projects = self.client.packages.discover.search(query)
                self.root.after(0, lambda: self.display_projects(projects))
            except Exception as e:
                self.root.after(0, lambda: self.show_projects_error(str(e)))
        
        thread = threading.Thread(target=search_thread, daemon=True)
        thread.start()
    
    def display_projects(self, projects: List[Dict[str, Any]]):
        """Display the loaded projects."""
        self.discovered_projects = projects
        
        # Clear loading message
        for widget in self.projects_display.winfo_children():
            widget.destroy()
        
        if not projects:
            ctk.CTkLabel(
                self.projects_display,
                text="No projects found"
            ).pack(pady=20)
            return
        
        # Display count
        count_label = ctk.CTkLabel(
            self.projects_display,
            text=f"Found {len(projects)} projects",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        count_label.pack(pady=10)
        
        # Display each project
        for project in projects:
            self.create_project_card(project)
    
    def create_project_card(self, project: Dict[str, Any]):
        """Create a card for a single project."""
        card = ctk.CTkFrame(self.projects_display)
        card.pack(fill="x", padx=10, pady=5)
        
        # Left side - project info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Project name (bold)
        name_label = ctk.CTkLabel(
            info_frame,
            text=project['path_with_namespace'],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        name_label.pack(anchor="w")
        
        # Description
        desc = project['description'] or 'No description'
        desc_label = ctk.CTkLabel(
            info_frame,
            text=desc[:80] + ('...' if len(desc) > 80 else ''),
            text_color="gray"
        )
        desc_label.pack(anchor="w", pady=(2, 0))
        
        # Metadata
        meta_text = f"⭐ {project['star_count']} | 📅 {project['last_activity_at'][:10]}"
        meta_label = ctk.CTkLabel(
            info_frame,
            text=meta_text,
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        meta_label.pack(anchor="w", pady=(2, 0))
        
        # Right side - action buttons
        actions_frame = ctk.CTkFrame(card)
        actions_frame.pack(side="right", padx=10, pady=10)
        
        # Select button
        select_btn = ctk.CTkButton(
            actions_frame,
            text="Select",
            command=lambda p=project: self.select_project(p),
            width=100,
            fg_color="green",
            hover_color="darkgreen"
        )
        select_btn.pack(pady=2)
        
        # View packages button
        packages_btn = ctk.CTkButton(
            actions_frame,
            text="Packages",
            command=lambda p=project: self.view_project_packages(p),
            width=100
        )
        packages_btn.pack(pady=2)
    
    def select_project(self, project: Dict[str, Any]):
        """Select a project and go to upload view."""
        self.current_project = project['path_with_namespace']
        messagebox.showinfo(
            "Project Selected",
            f"Selected: {self.current_project}\n\n"
            f"You can now upload packages to this project."
        )
        self.show_upload_view()
    
    def view_project_packages(self, project: Dict[str, Any]):
        """View packages for a selected project."""
        self.current_project = project['path_with_namespace']
        self.show_list_view()
    
    def show_projects_error(self, error_msg: str):
        """Show error when loading projects fails."""
        for widget in self.projects_display.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.projects_display,
            text=f"Error: {error_msg}",
            text_color="red"
        ).pack(pady=20)
    
    def show_upload_view(self):
        """Show the package upload interface."""
        self.clear_main_frame()
        
        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Upload Package",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Form frame
        form = ctk.CTkFrame(self.main_frame)
        form.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Project ID with browse button
        project_frame = ctk.CTkFrame(form)
        project_frame.pack(fill="x", padx=20, pady=(20, 5))
        
        ctk.CTkLabel(project_frame, text="Project:").pack(side="left", padx=(0, 10))
        
        self.upload_project_entry = ctk.CTkEntry(
            project_frame,
            placeholder_text="group/project"
        )
        self.upload_project_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Pre-fill if project selected
        if self.current_project:
            self.upload_project_entry.insert(0, self.current_project)
        
        browse_projects_btn = ctk.CTkButton(
            project_frame,
            text="Browse",
            command=self.show_project_browser,
            width=100
        )
        browse_projects_btn.pack(side="right")
        
        # File selection
        ctk.CTkLabel(form, text="File to Upload:").pack(anchor="w", padx=20, pady=(15, 5))
        
        file_frame = ctk.CTkFrame(form)
        file_frame.pack(fill="x", padx=20, pady=5)
        
        self.upload_file_entry = ctk.CTkEntry(file_frame, placeholder_text="Select a file...")
        self.upload_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            file_frame,
            text="Browse",
            command=self.browse_upload_file,
            width=100
        )
        browse_btn.pack(side="right")
        
        # Package name
        ctk.CTkLabel(form, text="Package Name (optional):").pack(anchor="w", padx=20, pady=(15, 5))
        self.upload_name_entry = ctk.CTkEntry(form, placeholder_text="Auto-detected from filename")
        self.upload_name_entry.pack(fill="x", padx=20, pady=5)
        
        # Package version
        ctk.CTkLabel(form, text="Package Version:").pack(anchor="w", padx=20, pady=(15, 5))
        self.upload_version_entry = ctk.CTkEntry(form, placeholder_text="1.0.0")
        self.upload_version_entry.pack(fill="x", padx=20, pady=5)
        self.upload_version_entry.insert(0, "1.0.0")
        
        # Progress bar
        self.upload_progress = ctk.CTkProgressBar(form)
        self.upload_progress.pack(fill="x", padx=20, pady=15)
        self.upload_progress.set(0)
        
        # Status label
        self.upload_status = ctk.CTkLabel(form, text="")
        self.upload_status.pack(pady=5)
        
        # Upload button
        upload_btn = ctk.CTkButton(
            form,
            text="Upload Package",
            command=self.upload_package,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        upload_btn.pack(pady=20)
    
    def browse_upload_file(self):
        """Open file browser to select file for upload."""
        filename = filedialog.askopenfilename(
            title="Select file to upload",
            filetypes=[
                ("All files", "*.*"),
                ("Archives", "*.tar.gz *.tar.bz2 *.zip"),
                ("Packages", "*.deb *.rpm *.whl"),
            ]
        )
        if filename:
            self.upload_file_entry.delete(0, tk.END)
            self.upload_file_entry.insert(0, filename)
    
    def upload_package(self):
        """Upload the selected package."""
        project_id = self.upload_project_entry.get().strip()
        file_path = self.upload_file_entry.get().strip()
        package_name = self.upload_name_entry.get().strip() or None
        package_version = self.upload_version_entry.get().strip()
        
        if not project_id:
            messagebox.showerror("Error", "Please enter a project ID/path or browse projects")
            return
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload")
            return
        
        if not package_version:
            messagebox.showerror("Error", "Please enter a package version")
            return
        
        # Update status
        self.upload_status.configure(text="Uploading...", text_color="yellow")
        self.upload_progress.set(0)
        
        # Progress callback
        def progress_callback(current, total):
            progress = current / total if total > 0 else 0
            self.upload_progress.set(progress)
            self.upload_status.configure(
                text=f"Uploading: {progress*100:.1f}%"
            )
            self.root.update()
        
        # Upload in thread
        def upload_thread():
            try:
                result = self.client.packages.upload(
                    project_id=project_id,
                    file_path=file_path,
                    package_name=package_name,
                    package_version=package_version,
                    progress_callback=progress_callback,
                )
                
                self.root.after(0, lambda: self.upload_complete(result))
                
            except ValidationError as e:
                self.root.after(0, lambda: self.upload_error(f"Validation error: {e}"))
            except ResourceNotFoundError as e:
                self.root.after(0, lambda: self.upload_error(f"Project not found: {e}"))
            except OperationError as e:
                self.root.after(0, lambda: self.upload_error(f"Upload failed: {e}"))
            except Exception as e:
                self.root.after(0, lambda: self.upload_error(f"Unexpected error: {e}"))
        
        thread = threading.Thread(target=upload_thread, daemon=True)
        thread.start()
    
    def upload_complete(self, result):
        """Handle successful upload."""
        self.upload_progress.set(1.0)
        self.upload_status.configure(
            text=f"✓ Upload complete! Package ID: {result.get('package_id', 'N/A')}",
            text_color="green"
        )
        messagebox.showinfo(
            "Success",
            f"Package uploaded successfully!\n\n"
            f"Name: {result['package_name']}\n"
            f"Version: {result['package_version']}\n"
            f"ID: {result.get('package_id', 'N/A')}"
        )
    
    def upload_error(self, error_msg):
        """Handle upload error."""
        self.upload_status.configure(text=f"✗ {error_msg}", text_color="red")
        messagebox.showerror("Upload Failed", error_msg)
    
    def show_list_view(self):
        """Show the package list interface."""
        self.clear_main_frame()
        
        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="List Packages",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(search_frame, text="Project:").pack(side="left", padx=10)
        
        self.list_project_entry = ctk.CTkEntry(search_frame, width=300)
        self.list_project_entry.pack(side="left", padx=10)
        
        # Pre-fill if project selected
        if self.current_project:
            self.list_project_entry.insert(0, self.current_project)
        
        list_btn = ctk.CTkButton(
            search_frame,
            text="Load Packages",
            command=self.load_packages,
            width=120
        )
        list_btn.pack(side="left", padx=10)
        
        browse_btn = ctk.CTkButton(
            search_frame,
            text="Browse Projects",
            command=self.show_project_browser,
            width=120
        )
        browse_btn.pack(side="left", padx=10)
        
        # NEW: Scan All Projects button
        scan_all_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Scan All Projects",
            command=self.scan_all_packages,
            width=160,
            fg_color="orange",
            hover_color="darkorange"
        )
        scan_all_btn.pack(side="right", padx=10)
        
        # Packages display area (scrollable)
        self.packages_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.packages_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def load_packages(self):
        """Load and display packages for the project."""
        project_id = self.list_project_entry.get().strip()
        
        if not project_id:
            messagebox.showerror("Error", "Please enter a project ID/path")
            return
        
        # Update current project
        self.current_project = project_id
        
        # Clear current packages
        for widget in self.packages_frame.winfo_children():
            widget.destroy()
        
        loading_label = ctk.CTkLabel(self.packages_frame, text="Loading packages...")
        loading_label.pack(pady=20)
        
        def load_thread():
            try:
                packages = self.client.packages.list(project_id)
                self.root.after(0, lambda: self.display_packages(packages))
            except Exception as e:
                self.root.after(0, lambda: self.show_load_error(str(e)))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def display_packages(self, packages):
        """Display the loaded packages."""
        # Clear loading message
        for widget in self.packages_frame.winfo_children():
            widget.destroy()
        
        if not packages:
            ctk.CTkLabel(
                self.packages_frame,
                text="No packages found in this project"
            ).pack(pady=20)
            return
        
        # Display each package
        for pkg in packages:
            pkg_frame = ctk.CTkFrame(self.packages_frame)
            pkg_frame.pack(fill="x", padx=10, pady=5)
            
            # Package info
            info_text = f"{pkg['name']} v{pkg['version']} ({pkg['package_type']})"
            ctk.CTkLabel(
                pkg_frame,
                text=info_text,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=10)
            
            # Created date
            ctk.CTkLabel(
                pkg_frame,
                text=f"Created: {pkg['created_at'][:10]}",
                text_color="gray"
            ).pack(side="left", padx=10)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                pkg_frame,
                text="Delete",
                command=lambda p=pkg: self.delete_package(p),
                width=80,
                fg_color="red",
                hover_color="darkred"
            )
            delete_btn.pack(side="right", padx=10)
    
    def delete_package(self, package):
        """Delete a package."""
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete:\n\n"
            f"{package['name']} v{package['version']}?"
        )
        
        if confirm:
            try:
                project_id = self.list_project_entry.get().strip()
                self.client.packages.delete(project_id, package['id'])
                messagebox.showinfo("Success", "Package deleted successfully")
                self.load_packages()  # Refresh list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete package: {e}")
    
    def show_load_error(self, error_msg):
        """Show error when loading packages fails."""
        for widget in self.packages_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.packages_frame,
            text=f"Error loading packages: {error_msg}",
            text_color="red"
        ).pack(pady=20)
    
    def scan_all_packages(self):
        """Scan all owned projects for packages and display in tree view."""
        # Clear current display
        for widget in self.packages_frame.winfo_children():
            widget.destroy()
        
        # Show scanning status
        status_frame = ctk.CTkFrame(self.packages_frame)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.scan_status_label = ctk.CTkLabel(
            status_frame,
            text="Scanning all projects...",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.scan_status_label.pack(pady=10)
        
        self.scan_progress_label = ctk.CTkLabel(
            status_frame,
            text="Finding projects...",
            text_color="gray"
        )
        self.scan_progress_label.pack()
        
        # Progress bar
        self.scan_progress_bar = ctk.CTkProgressBar(status_frame)
        self.scan_progress_bar.pack(fill="x", padx=20, pady=10)
        self.scan_progress_bar.set(0)
        
        # Run scan in thread
        def scan_thread():
            try:
                # Get all owned projects
                self.root.after(0, lambda: self.scan_progress_label.configure(
                    text="Loading your projects..."
                ))
                
                projects = self.client.packages.discover.list_all()
                total_projects = len(projects)
                
                self.root.after(0, lambda: self.scan_status_label.configure(
                    text=f"Scanning {total_projects} projects for packages..."
                ))
                
                # Scan each project for packages
                all_packages = {}
                projects_with_packages = 0
                total_packages = 0
                
                for i, project in enumerate(projects):
                    try:
                        # Update progress
                        progress = (i + 1) / total_projects
                        self.root.after(0, lambda p=progress, prj=project: (
                            self.scan_progress_bar.set(p),
                            self.scan_progress_label.configure(
                                text=f"Scanning: {prj['path_with_namespace']} ({i+1}/{total_projects})"
                            )
                        ))
                        
                        # Get packages for this project
                        packages = self.client.packages.list(project['id'])
                        
                        if packages:
                            all_packages[project['path_with_namespace']] = {
                                'project': project,
                                'packages': packages,
                            }
                            projects_with_packages += 1
                            total_packages += len(packages)
                        
                    except Exception as e:
                        # Skip projects that error (e.g., no access to packages)
                        print(f"Error scanning {project['path_with_namespace']}: {e}")
                        continue
                
                # Display results
                self.root.after(0, lambda: self.display_package_tree(
                    all_packages,
                    total_projects,
                    projects_with_packages,
                    total_packages
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_scan_error(str(e)))
        
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
    
    def display_package_tree(
        self,
        all_packages: Dict[str, Any],
        total_projects: int,
        projects_with_packages: int,
        total_packages: int
    ):
        """Display packages in a tree structure."""
        # Clear scanning status
        for widget in self.packages_frame.winfo_children():
            widget.destroy()
        
        # Summary header - compact, fixed height
        summary_frame = ctk.CTkFrame(self.packages_frame)
        summary_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        summary_text = (
            f"📊 Scanned {total_projects} projects | "
            f"📦 Found {total_packages} packages in {projects_with_packages} projects"
        )
        
        ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=8)
        
        # Filter/search for tree - compact, fixed height
        filter_frame = ctk.CTkFrame(self.packages_frame)
        filter_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=5)
        
        self.tree_filter_entry = ctk.CTkEntry(filter_frame, width=200)
        self.tree_filter_entry.pack(side="left", padx=5)
        
        filter_btn = ctk.CTkButton(
            filter_frame,
            text="Apply Filter",
            command=lambda: self.filter_package_tree(all_packages),
            width=100
        )
        filter_btn.pack(side="left", padx=5)
        
        clear_filter_btn = ctk.CTkButton(
            filter_frame,
            text="Clear",
            command=lambda: (
                self.tree_filter_entry.delete(0, tk.END),
                self.filter_package_tree(all_packages)
            ),
            width=80
        )
        clear_filter_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = ctk.CTkButton(
            filter_frame,
            text="📋 Export",
            command=lambda: self.export_package_tree(all_packages),
            width=100
        )
        export_btn.pack(side="right", padx=5)
        
        # Tree display area - Calculate height based on window size
        # Subtract space for: title(40) + search_frame(80) + summary(60) + filter(60) + padding(80)
        # Total overhead: ~320px, so tree gets remaining space
        window_height = self.root.winfo_height()
        tree_height = max(400, window_height - 320)  # At least 400px, more if window is larger
        
        tree_area = ctk.CTkScrollableFrame(self.packages_frame, height=tree_height)
        tree_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Store for filtering
        self.tree_area = tree_area
        self.all_packages_data = all_packages
        
        # Display tree
        self.render_package_tree(tree_area, all_packages)
    
    def render_package_tree(self, parent, all_packages: Dict[str, Any], filter_text: str = ""):
        """Render the package tree structure."""
        # Clear current tree
        for widget in parent.winfo_children():
            widget.destroy()
        
        if not all_packages:
            ctk.CTkLabel(
                parent,
                text="No packages found in any projects",
                text_color="gray"
            ).pack(pady=20)
            return
        
        filter_lower = filter_text.lower()
        
        # Group by namespace for better organization
        by_namespace = {}
        for project_path, data in all_packages.items():
            namespace = project_path.split('/')[0] if '/' in project_path else 'root'
            if namespace not in by_namespace:
                by_namespace[namespace] = {}
            by_namespace[namespace][project_path] = data
        
        # Render tree by namespace
        for namespace in sorted(by_namespace.keys()):
            # Apply filter
            namespace_packages = by_namespace[namespace]
            if filter_lower:
                # Filter packages
                filtered_namespace = {}
                for proj_path, data in namespace_packages.items():
                    filtered_pkgs = [
                        pkg for pkg in data['packages']
                        if filter_lower in pkg['name'].lower() or
                           filter_lower in pkg['package_type'].lower() or
                           filter_lower in proj_path.lower()
                    ]
                    if filtered_pkgs:
                        filtered_namespace[proj_path] = {
                            'project': data['project'],
                            'packages': filtered_pkgs,
                        }
                namespace_packages = filtered_namespace
            
            if not namespace_packages:
                continue
            
            # Create namespace section
            self.create_namespace_section(parent, namespace, namespace_packages)
    
    def create_namespace_section(self, parent, namespace: str, projects: Dict[str, Any]):
        """Create a collapsible namespace section."""
        # Namespace header (collapsible)
        namespace_frame = ctk.CTkFrame(parent)
        namespace_frame.pack(fill="x", padx=5, pady=5)
        
        # Count packages in this namespace
        total_ns_packages = sum(len(data['packages']) for data in projects.values())
        
        # Create a frame to hold the toggle state
        is_expanded = tk.BooleanVar(value=True)
        
        header = ctk.CTkFrame(namespace_frame)
        header.pack(fill="x", padx=5, pady=5)
        
        # Toggle button
        toggle_btn = ctk.CTkButton(
            header,
            text="▼",
            width=30,
            command=lambda: self.toggle_namespace(namespace_frame, is_expanded, toggle_btn)
        )
        toggle_btn.pack(side="left", padx=(5, 10))
        
        # Namespace label
        ns_label = ctk.CTkLabel(
            header,
            text=f"📁 {namespace}  ({len(projects)} projects, {total_ns_packages} packages)",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        ns_label.pack(side="left")
        
        # Content frame (projects and packages)
        content_frame = ctk.CTkFrame(namespace_frame)
        content_frame.pack(fill="x", padx=20, pady=5)
        
        # Store reference for toggling
        namespace_frame.content_frame = content_frame
        
        # Render projects in this namespace
        for project_path in sorted(projects.keys()):
            data = projects[project_path]
            self.create_project_section(content_frame, project_path, data)
    
    def create_project_section(self, parent, project_path: str, data: Dict[str, Any]):
        """Create a collapsible project section."""
        project = data['project']
        packages = data['packages']
        
        # Project frame
        project_frame = ctk.CTkFrame(parent)
        project_frame.pack(fill="x", padx=5, pady=3)
        
        is_expanded = tk.BooleanVar(value=False)  # Collapsed by default
        
        header = ctk.CTkFrame(project_frame)
        header.pack(fill="x", padx=5, pady=5)
        
        # Toggle button
        toggle_btn = ctk.CTkButton(
            header,
            text="▶",
            width=30,
            command=lambda: self.toggle_project(project_frame, is_expanded, toggle_btn)
        )
        toggle_btn.pack(side="left", padx=(5, 10))
        
        # Project label
        proj_label = ctk.CTkLabel(
            header,
            text=f"📦 {project['path']}  ({len(packages)} packages)",
            font=ctk.CTkFont(size=12)
        )
        proj_label.pack(side="left")
        
        # Quick action buttons
        actions = ctk.CTkFrame(header)
        actions.pack(side="right", padx=5)
        
        view_btn = ctk.CTkButton(
            actions,
            text="View",
            width=60,
            command=lambda: self.view_project_from_tree(project_path),
            height=25
        )
        view_btn.pack(side="left", padx=2)
        
        # Content frame (packages)
        content_frame = ctk.CTkFrame(project_frame)
        # Don't pack yet - will be shown on toggle
        
        project_frame.content_frame = content_frame
        
        # Render packages (but hidden initially)
        for pkg in packages:
            self.create_package_item(content_frame, pkg, project_path)
    
    def create_package_item(self, parent, package: Dict[str, Any], project_path: str):
        """Create a single package item."""
        pkg_frame = ctk.CTkFrame(parent)
        pkg_frame.pack(fill="x", padx=5, pady=2)
        
        # Package icon based on type
        type_icons = {
            'generic': '📄',
            'pypi': '🐍',
            'npm': '📦',
            'maven': '☕',
            'nuget': '◆',
            'composer': '🎵',
            'conan': '🔧',
        }
        icon = type_icons.get(package['package_type'], '📦')
        
        # Package info
        info = ctk.CTkLabel(
            pkg_frame,
            text=f"  {icon} {package['name']} v{package['version']}",
            font=ctk.CTkFont(size=11)
        )
        info.pack(side="left", padx=10, pady=5)
        
        # Package type badge
        type_badge = ctk.CTkLabel(
            pkg_frame,
            text=package['package_type'],
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        type_badge.pack(side="left", padx=5)
        
        # Created date
        date_label = ctk.CTkLabel(
            pkg_frame,
            text=f"📅 {package['created_at'][:10]}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        date_label.pack(side="left", padx=10)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            pkg_frame,
            text="🗑️",
            width=30,
            height=25,
            command=lambda: self.delete_package_from_tree(project_path, package),
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.pack(side="right", padx=5)
    
    def toggle_namespace(self, frame, is_expanded: tk.BooleanVar, button):
        """Toggle namespace expansion."""
        if is_expanded.get():
            # Collapse
            frame.content_frame.pack_forget()
            button.configure(text="▶")
            is_expanded.set(False)
        else:
            # Expand
            frame.content_frame.pack(fill="x", padx=20, pady=5)
            button.configure(text="▼")
            is_expanded.set(True)
    
    def toggle_project(self, frame, is_expanded: tk.BooleanVar, button):
        """Toggle project expansion."""
        if is_expanded.get():
            # Collapse
            frame.content_frame.pack_forget()
            button.configure(text="▶")
            is_expanded.set(False)
        else:
            # Expand
            frame.content_frame.pack(fill="x", padx=20, pady=5)
            button.configure(text="▼")
            is_expanded.set(True)
    
    def filter_package_tree(self, all_packages: Dict[str, Any]):
        """Apply filter to package tree."""
        filter_text = self.tree_filter_entry.get().strip()
        self.render_package_tree(self.tree_area, all_packages, filter_text)
    
    def view_project_from_tree(self, project_path: str):
        """View a project's packages from the tree."""
        self.current_project = project_path
        self.list_project_entry.delete(0, tk.END)
        self.list_project_entry.insert(0, project_path)
        self.load_packages()
    
    def delete_package_from_tree(self, project_path: str, package: Dict[str, Any]):
        """Delete a package from the tree view."""
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete package from {project_path}?\n\n"
            f"{package['name']} v{package['version']}"
        )
        
        if confirm:
            try:
                self.client.packages.delete(project_path, package['id'])
                messagebox.showinfo("Success", "Package deleted")
                # Rescan to refresh tree
                self.scan_all_packages()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
    
    def export_package_tree(self, all_packages: Dict[str, Any]):
        """Export package tree to a text file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown", "*.md"),
                ("All files", "*.*")
            ],
            title="Export Package Tree"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w') as f:
                f.write("GitLab Package Inventory\n")
                f.write("=" * 60 + "\n\n")
                
                # Group by namespace
                by_namespace = {}
                for project_path, data in all_packages.items():
                    namespace = project_path.split('/')[0] if '/' in project_path else 'root'
                    if namespace not in by_namespace:
                        by_namespace[namespace] = {}
                    by_namespace[namespace][project_path] = data
                
                # Write tree
                for namespace in sorted(by_namespace.keys()):
                    total_packages = sum(
                        len(data['packages'])
                        for data in by_namespace[namespace].values()
                    )
                    
                    f.write(f"\n{namespace}/ ({total_packages} packages)\n")
                    f.write("-" * 60 + "\n")
                    
                    for project_path in sorted(by_namespace[namespace].keys()):
                        data = by_namespace[namespace][project_path]
                        f.write(f"\n  {project_path} ({len(data['packages'])} packages)\n")
                        
                        for pkg in data['packages']:
                            f.write(f"    - {pkg['name']} v{pkg['version']} ")
                            f.write(f"({pkg['package_type']}) ")
                            f.write(f"[{pkg['created_at'][:10]}]\n")
            
            messagebox.showinfo(
                "Export Successful",
                f"Package tree exported to:\n{filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {e}")
    
    def show_scan_error(self, error_msg: str):
        """Show error when scanning fails."""
        for widget in self.packages_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.packages_frame,
            text=f"Error scanning projects: {error_msg}",
            text_color="red"
        ).pack(pady=20)
    
    def show_download_view(self):
        """Show the download interface."""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="Download Package",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        ctk.CTkLabel(
            self.main_frame,
            text="Download feature coming soon!",
            font=ctk.CTkFont(size=14)
        ).pack(pady=40)
    
    def show_search_view(self):
        """Show the search interface."""
        self.clear_main_frame()
        
        title = ctk.CTkLabel(
            self.main_frame,
            text="Search Packages",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        ctk.CTkLabel(
            self.main_frame,
            text="Search feature coming soon!",
            font=ctk.CTkFont(size=14)
        ).pack(pady=40)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    app = PackageManagerGUI()
    app.run()


if __name__ == '__main__':
    main()