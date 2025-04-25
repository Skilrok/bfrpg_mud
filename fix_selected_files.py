#!/usr/bin/env python3
"""
Script to fix CI/CO issues for selected files only, to avoid overwhelming errors.
This script formats and fixes linting issues in a controlled manner.
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, file_path=None):
    """Run a command and return whether it succeeded"""
    command = cmd + ([str(file_path)] if file_path else [])
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ Successfully processed {file_path if file_path else ''}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def fix_file(file_path):
    """Apply fixes to a single file"""
    print(f"\nProcessing file: {file_path}")
    
    # Try running black first
    if not run_command(["black", "--line-length=88"], file_path):
        print(f"Skipping further processing for {file_path}")
        return False
    
    # Then run isort
    if not run_command(["isort", "--profile=black"], file_path):
        print(f"Warning: isort failed for {file_path}")
    
    return True

def main():
    """Main function"""
    print("Starting file-by-file fixes...")
    
    # Check if black and isort are installed
    try:
        import black
        import isort
    except ImportError:
        print("Error: black or isort not installed. Please install them with:")
        print("pip install black isort")
        return 1
    
    # List of priority files to fix - start with a small set
    priority_files = [
        # Core files
        Path("app/models/character.py"),
        Path("app/models/hireling.py"),
        Path("app/models/item.py"),
        Path("app/routers/characters.py"),
        Path("app/routers/hirelings.py"),
        Path("app/schemas/character.py"),
        Path("app/schemas/hireling.py"),
        Path("app/schemas/item.py"),
        Path("fix_character_owner_relationship.py"),
        Path("rename_hireling_column.py")
    ]
    
    # Track success/failure
    fixed = []
    failed = []
    
    # Process each file
    for file_path in priority_files:
        if not file_path.exists():
            print(f"Warning: File {file_path} not found, skipping.")
            continue
        
        if fix_file(file_path):
            fixed.append(file_path)
        else:
            failed.append(file_path)
    
    # Print summary
    print("\n--- Summary ---")
    print(f"Successfully fixed: {len(fixed)} files")
    print(f"Failed to fix: {len(failed)} files")
    
    if failed:
        print("\nFailed files:")
        for file in failed:
            print(f"- {file}")
    
    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main()) 