#!/usr/bin/env python3
"""
Launch the GitLab Package Manager GUI.

Simple launcher script that can be run from anywhere.
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    
    try:
        import gitlabmanager
    except ImportError:
        missing.append("gitlabmanager")
    
    if missing:
        print("Missing required dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall them with:")
        print("   pip install customtkinter")
        print("   pip install -e .[gui]")
        sys.exit(1)


def main():
    """Main launcher function."""
    print("=" * 60)
    print("GitLab Package Manager GUI")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    print("\nAll dependencies found")
    print("Launching GUI...\n")
    
    # Import and run GUI
    try:
        from gui.package_manager_gui import PackageManagerGUI
        
        app = PackageManagerGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nGUI closed by user")
    except Exception as e:
        print(f"\nError launching GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()