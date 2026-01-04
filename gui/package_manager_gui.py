"""
GitLab Package Manager GUI using CustomTkinter.

A modern, user-friendly interface for managing GitLab packages.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Optional
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
        self.root.geometry("1000x700")
        
        # GitLab client (will be initialized after login)
        self.client: Optional[GitLabClient] = None
        self.current_project: Optional[str] = None
        
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
        
        # Show upload view by default
        self.show_upload_view()
    
    def create_sidebar(self):
        """Create the sidebar with navigation."""
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            sidebar,
            text="Package Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=20)
        
        # Navigation buttons
        upload_btn = ctk.CTkButton(
            sidebar,
            text="📤 Upload",
            command=self.show_upload_view,
            width=160
        )
        upload_btn.grid(row=1, column=0, padx=20, pady=10)
        
        list_btn = ctk.CTkButton(
            sidebar,
            text="📋 List Packages",
            command=self.show_list_view,
            width=160
        )
        list_btn.grid(row=2, column=0, padx=20, pady=10)
        
        download_btn = ctk.CTkButton(
            sidebar,
            text="📥 Download",
            command=self.show_download_view,
            width=160
        )
        download_btn.grid(row=3, column=0, padx=20, pady=10)
        
        search_btn = ctk.CTkButton(
            sidebar,
            text="🔍 Search",
            command=self.show_search_view,
            width=160
        )
        search_btn.grid(row=4, column=0, padx=20, pady=10)
        
        # Disconnect button at bottom
        disconnect_btn = ctk.CTkButton(
            sidebar,
            text="🔌 Disconnect",
            command=self.create_login_screen,
            width=160,
            fg_color="gray"
        )
        disconnect_btn.grid(row=7, column=0, padx=20, pady=20)
    
    def clear_main_frame(self):
        """Clear the main content area."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
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
        
        # Project ID
        ctk.CTkLabel(form, text="Project ID/Path:").pack(anchor="w", padx=20, pady=(20, 5))
        self.upload_project_entry = ctk.CTkEntry(form, placeholder_text="group/project")
        self.upload_project_entry.pack(fill="x", padx=20, pady=5)
        
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
            messagebox.showerror("Error", "Please enter a project ID/path")
            return
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload")
            return
        
        if not package_version:
            messagebox.showerror("Error", "Please enter a package version")
            return
        
        # Disable upload button during upload
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
        
        # Upload in thread to prevent UI freeze
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
        
        ctk.CTkLabel(search_frame, text="Project ID/Path:").pack(side="left", padx=10)
        
        self.list_project_entry = ctk.CTkEntry(search_frame, width=300)
        self.list_project_entry.pack(side="left", padx=10)
        
        list_btn = ctk.CTkButton(
            search_frame,
            text="Load Packages",
            command=self.load_packages,
            width=120
        )
        list_btn.pack(side="left", padx=10)
        
        # Packages display area (scrollable)
        self.packages_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.packages_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
    def load_packages(self):
        """Load and display packages for the project."""
        project_id = self.list_project_entry.get().strip()
        
        if not project_id:
            messagebox.showerror("Error", "Please enter a project ID/path")
            return
        
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