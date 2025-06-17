import os
import json
import difflib
import re

#matches for empty lines, "import", any comment "/*", and closing braces (})
pattern = re.compile(r'^(?:\s*$|import\b|.*\/\*.*|\s*\*|\s*\})')

def extract_new_changes(old_lines, new_lines):

    #get list of differences
    diff = list(difflib.ndiff(old_lines, new_lines))
    new_changes = []  #list of tuples (new_line_index, content)
    new_index = 0  #get index to check whether method belongs to a new class

    for line in diff:
        if line.startswith('+ '):
            content = line[2:].strip()
            if not pattern.match(content):
                new_changes.append((new_index, content))

        #increase line counter
        if line.startswith('  ') or line.startswith('+ '):
            new_index += 1

    #creates a list to get the position of every class
    class_positions = []
    for i, line in enumerate(new_lines):

        if re.search(r'\bclass\b', line):
            class_positions.append((i, line.strip()))

    new_classes = {}
    #for new methods that have been added to an existing class
    new_methods = []

    for idx, content in new_changes:
        if re.search(r'\bclass\b', content):
            new_classes[idx] = {"declaration": content, "methods": []}

    for idx, content in new_changes:
        if re.search(r'\bclass\b', content):
            continue  #already handled

        parent_class_idx = None
        for pos, decl in class_positions:
            if pos <= idx:
                parent_class_idx = pos
            else:
                break

        if parent_class_idx is not None and parent_class_idx in new_classes:
            new_classes[parent_class_idx]["methods"].append(content)
        else:
            new_methods.append(content)

    return {
        "new_classes": list(new_classes.values()),
        "new_methods": new_methods
    }

#https://stackoverflow.com/questions/8625991/use-python-os-walk-to-identify-a-list-of-files
#get all java files in every subdirectory of results (after minimization is performed)
def list_java_files(directory):
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            java_files.append(relative_path)

    #list of relative path of every file
    return java_files

def read_file_lines(filepath):

    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()

#https://docs.python.org/3/library/difflib.html
#uses python's difflib to compare two lines at a time
def extract_new_lines(old_lines, new_lines):

    diff = difflib.ndiff(old_lines, new_lines)
    newly_added = []

    for line in diff:
        #new lines will start with +
        if line.startswith('+ '):
            content = line[2:].strip()
            #makes sure a new line passes regex check before appending
            if not pattern.match(content):
                newly_added.append(content)
    return newly_added

#returns a dictionary of new changes between subsequent JDK versions
def compare_version_pair(old_version_dir, new_version_dir):
    new_files = list_java_files(new_version_dir)
    file_diff = {}

    for rel_path in new_files:
        #generates github URL
        branch = os.path.basename(new_version_dir)
        url = f"https://github.com/eisop/jdk/tree/{branch}"
        parts = rel_path.split(os.path.sep)
        url = url + '/' + '/'.join(parts[1:])

        new_file_path = os.path.join(new_version_dir, rel_path)
        old_file_path = os.path.join(old_version_dir, rel_path)

        if os.path.exists(old_file_path):
            old_lines = read_file_lines(old_file_path)
        else:
            old_lines = []

        new_lines = read_file_lines(new_file_path)

        changes = extract_new_changes(old_lines, new_lines)
        if changes["new_classes"] or changes["new_methods"]:
            file_diff[url] = {
                "new_changes": changes
            }
    return file_diff

#this list must be modified for newly added jdk versions
versions = ['master', 'jdk-18', 'jdk-19', 'jdk-20', 'jdk-21', 'jdk-22', 'jdk-23', 'jdk-24']

base_path = './results/'

json_folder = "../report-files/json_files"
os.makedirs(json_folder, exist_ok=True)

#compares all subsequent versions, creates a seperate json file for each version pair
for i in range(1, len(versions)):

    results = {}

    old_version = versions[i - 1]
    new_version = versions[i]

    version_pair_key = new_version

    old_dir = os.path.join(base_path, old_version)
    new_dir = os.path.join(base_path, new_version)

    current_diff = compare_version_pair(old_dir, new_dir)
    results[version_pair_key] = current_diff

    current_json = os.path.join(json_folder, f"{versions[i]}.json")

    with open(current_json, 'w', encoding='utf-8') as out_f:
        json.dump(results, out_f, indent=2)

    print(f"Created json for {old_version} -> {new_version}")