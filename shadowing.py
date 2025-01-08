import os

def check_for_shadowing(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if 'requests' in line:
                            print(f"Found 'requests' in {file_path} at line {i + 1}: {line.strip()}")
                        if 'import requests' not in lines and 'requests' in line:
                            print(f"Potential issue: 'requests' used but not imported in {file_path} at line {i + 1}: {line.strip()}")

# Replace 'your_project_directory' with the path to your project directory
check_for_shadowing('/Users/minervae/Library/Mobile Documents/com~apple~CloudDocs/___WORK/__DEUTSCH/_GDocs-Content/__ANKI-cards/txt-to-ANKI')

# Redirect output to a file
output_file = '/archive/shadow-log.txt'
with open(output_file, 'w') as f:
    import sys
    sys.stdout = f
    check_for_shadowing('/Users/minervae/Library/Mobile Documents/com~apple~CloudDocs/___WORK/__DEUTSCH/_GDocs-Content/__ANKI-cards/txt-to-ANKI')
    sys.stdout = sys.__stdout__