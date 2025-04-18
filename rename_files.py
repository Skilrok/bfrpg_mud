import os
import re

# Directory containing the files
directory = 'docs/bfsrd'

# Get all files in the directory
files = os.listdir(directory)

# Regex pattern to match 'www_basicfantasy_org_' prefix and '_html' suffix
pattern = r'^www_basicfantasy_org_(.*?)_html\.md$'
pattern_no_html = r'^www_basicfantasy_org_(.*?)\.md$'  # For special case like srd.md

# Track renamed files
renamed_files = []

# Process each file
for filename in files:
    # Check if file matches the pattern
    match = re.match(pattern, filename)
    if match:
        # Extract the middle part (without prefix and suffix)
        new_name = match.group(1) + '.md'
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        
        # Rename the file
        os.rename(old_path, new_path)
        renamed_files.append((filename, new_name))
    else:
        # Check for special case (no _html suffix)
        match_no_html = re.match(pattern_no_html, filename)
        if match_no_html:
            new_name = match_no_html.group(1) + '.md'
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_name)
            
            # Rename the file
            os.rename(old_path, new_path)
            renamed_files.append((filename, new_name))

# Print out the renamed files
print(f"Renamed {len(renamed_files)} files:")
for old, new in renamed_files:
    print(f"  {old} → {new}") 