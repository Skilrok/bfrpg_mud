#!/usr/bin/env python3
"""
Script to fix CI/CO issues by automatically formatting all Python files
and addressing common linting issues.
"""

import os
import subprocess
import sys

# REMOVED: from pathlib import Path


def run_command(command):
    """Run a shell command and print the output"""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def find_python_files():
    """Find all Python files in the project excluding migrations and venv"""
    python_files = []
    exclude_dirs = {".git", ".venv", "venv", "env", "__pycache__"}
    exclude_migrations = {"migrations", "alembic"}

    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if d not in exclude_dirs and not any(m in root for m in exclude_migrations)
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def format_python_files(files):
    """Format Python files using black and isort"""
    print(f"Found {len(files)} Python files to format")

    # Run black
    if not run_command(["black", "--line-length=88"] + files):
        print("Error running black")
        return False

    # Run isort
    if not run_command(["isort", "--profile=black"] + files):
        print("Error running isort")
        return False

    return True


def main():
    """Main function"""
    print("Starting CI/CO fix script...")

    # Check if black and isort are installed
    try:
        import black
        import isort
    except ImportError:
        print("Error: black or isort not installed. Please install them with:")
        print("pip install black isort")
        return 1

    # Find Python files
    python_files = find_python_files()

    # Format files
    if not format_python_files(python_files):
        return 1

    print("\nFormatting complete! Next steps:")
    print(
        "1. Run 'flake8 --max-line-length=88 --extend-ignore=E203' to identify remaining issues"
    )
    print("2. Fix unused imports (F401) and long lines (E501) manually")
    print("3. Try a test commit to see if pre-commit hooks pass")

    return 0


if __name__ == "__main__":
    sys.exit(main())
