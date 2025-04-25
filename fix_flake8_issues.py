#!/usr/bin/env python3
"""
Script to fix common flake8 issues automatically.
Focuses on unused imports (F401) and over-length lines (E501).
"""

# REMOVED: import os
import re
import subprocess
import sys

# REMOVED: from pathlib import Path
from typing import Dict, List, Set, Tuple


def run_flake8(files=None):
    """Run flake8 and parse the output to get error information"""
    cmd = ["flake8", "--max-line-length=88", "--extend-ignore=E203"]

    if files:
        cmd.extend(files)

    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return result.stdout
    except subprocess.SubprocessError as e:
        print(f"Error running flake8: {e}")
        return ""


def parse_flake8_output(output: str) -> Dict[str, List[Tuple[int, str, str]]]:
    """Parse flake8 output and group issues by file"""
    issues_by_file = {}

    # Simple regex to parse flake8 output lines (file:line:col: error)
    pattern = r"(.+?):(\d+):(\d+): ([A-Z]\d+) (.*)"

    for line in output.splitlines():
        match = re.match(pattern, line)
        if match:
            file_path, line_num, col, error_code, message = match.groups()
            line_num = int(line_num)

            if file_path not in issues_by_file:
                issues_by_file[file_path] = []

            issues_by_file[file_path].append((line_num, error_code, message))

    return issues_by_file


def remove_unused_imports(file_path: str, issues: List[Tuple[int, str, str]]):
    """Remove unused imports from a file"""
    # Get only F401 issues (unused imports)
    unused_imports = [(line, msg) for line, code, msg in issues if code == "F401"]

    if not unused_imports:
        return False

    print(f"Fixing unused imports in {file_path}")

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Track which lines to remove or modify
    modified = False

    # Group by line numbers to handle multiple imports on the same line
    by_line = {}
    for line_num, msg in unused_imports:
        if line_num not in by_line:
            by_line[line_num] = []

        # Extract the import name from the message
        import_match = re.search(r"'(.+?)' imported but unused", msg)
        if import_match:
            by_line[line_num].append(import_match.group(1))

    # Process each line with unused imports
    for line_num, unused_names in by_line.items():
        line_idx = line_num - 1  # Convert to 0-based index
        line = lines[line_idx]

        if "import " not in line:
            continue

        # For simple import statements: "import module" or "from module import name"
        if re.match(r"\s*import\s+\w+\s*$", line) or re.match(
            r"\s*from\s+.+\s+import\s+\w+\s*$", line
        ):
            # Remove the entire line if it's a simple import that's unused
            lines[line_idx] = f"# REMOVED: {line}"
            modified = True

        # For multiple imports: "from module import name1, name2, name3"
        elif "from " in line and ", " in line:
            # Get all names being imported
            from_import_match = re.match(r"\s*from\s+.+\s+import\s+(.+)", line)
            if from_import_match:
                imports_str = from_import_match.group(1)

                # Split by comma and remove whitespace
                imports = [imp.strip() for imp in imports_str.split(",")]

                # Filter out unused imports
                used_imports = [imp for imp in imports if imp not in unused_names]

                if used_imports:
                    # Reconstruct the line with only used imports
                    imports_part = ", ".join(used_imports)
                    new_line = line.replace(imports_str, imports_part)
                    lines[line_idx] = new_line
                else:
                    # If all imports are unused, comment out the line
                    lines[line_idx] = f"# REMOVED: {line}"

                modified = True

    # Write changes back to the file
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"  Fixed {len(by_line)} line(s) with unused imports")
        return True

    return False


def fix_line_length_issues(file_path: str, issues: List[Tuple[int, str, str]]):
    """Attempt to fix line length issues by breaking long lines"""
    # Get only E501 issues (line too long)
    long_lines = [(line, msg) for line, code, msg in issues if code == "E501"]

    if not long_lines:
        return False

    print(f"Fixing line length issues in {file_path}")
    print("  Note: This is best effort - manual review recommended")

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False

    for line_num, _ in long_lines:
        line_idx = line_num - 1  # Convert to 0-based index
        line = lines[line_idx]

        # Try to break the line if it's a long string
        if '"' in line or "'" in line:
            # Don't try to fix f-strings or complex expressions
            if 'f"' in line or "f'" in line:
                continue

            # Simple string concatenation for literal strings
            matches = re.findall(r'([\'"].*?[\'"])', line)
            if len(matches) == 1 and len(matches[0]) > 40:
                parts = []
                current_part = ""

                # Try to break at spaces for readability
                words = matches[0].split()

                for word in words:
                    if len(current_part) + len(word) + 1 > 60:  # +1 for space
                        parts.append(current_part.rstrip())
                        current_part = word + " "
                    else:
                        current_part += word + " "

                if current_part:
                    parts.append(current_part.rstrip())

                if len(parts) > 1:
                    # Replace the long string with concatenated parts
                    new_line = line.replace(
                        matches[0], '" +\n' + " " * 12 + '"'.join(parts)
                    )
                    lines[line_idx] = new_line
                    modified = True

    # Write changes back to the file
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"  Fixed {len(long_lines)} line length issues")
        return True

    return False


def fix_bare_except(file_path: str, issues: List[Tuple[int, str, str]]):
    """Fix bare except statements (E722)"""
    # Get only E722 issues (bare except)
    bare_excepts = [(line, msg) for line, code, msg in issues if code == "E722"]

    if not bare_excepts:
        return False

    print(f"Fixing bare except statements in {file_path}")

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False

    for line_num, _ in bare_excepts:
        line_idx = line_num - 1  # Convert to 0-based index
        line = lines[line_idx]

        # Replace "except:" with "except Exception:"
        if re.search(r"\s*except\s*:", line):
            lines[line_idx] = line.replace("except:", "except Exception:")
            modified = True

    # Write changes back to the file
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"  Fixed {len(bare_excepts)} bare except statements")
        return True

    return False


def main():
    """Main function"""
    print("Starting flake8 issue fix script...")

    # Run flake8 to get issues
    flake8_output = run_flake8()

    if not flake8_output:
        print("No flake8 issues found or error running flake8.")
        return 0

    # Parse flake8 output
    issues_by_file = parse_flake8_output(flake8_output)

    if not issues_by_file:
        print("No issues parsed from flake8 output.")
        return 0

    print(f"Found issues in {len(issues_by_file)} files")

    # Fix issues in each file
    files_modified = 0

    for file_path, issues in issues_by_file.items():
        modified = False

        # Fix unused imports
        if remove_unused_imports(file_path, issues):
            modified = True

        # Fix bare except statements
        if fix_bare_except(file_path, issues):
            modified = True

        # Fix line length issues
        if fix_line_length_issues(file_path, issues):
            modified = True

        if modified:
            files_modified += 1

    print(f"\nFixed issues in {files_modified} files")
    print("\nNext steps:")
    print("1. Run the fix_ci_issues.py script to format files")
    print("2. Manually check the changes made")
    print("3. Try a test commit to see if pre-commit hooks pass")

    return 0


if __name__ == "__main__":
    sys.exit(main())
