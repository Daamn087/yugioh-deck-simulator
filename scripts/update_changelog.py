import os
import subprocess
import sys
from datetime import datetime
import re

CHANGELOG_PATH = "CHANGELOG.md"

def get_staged_files():
    try:
        output = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True)
        return output.splitlines()
    except subprocess.CalledProcessError:
        return []

def get_current_version():
    if not os.path.exists(CHANGELOG_PATH):
        return "0.0.0"
    
    with open(CHANGELOG_PATH, "r") as f:
        content = f.read()
        # Look for the first version pattern: ## [X.Y.Z]
        match = re.search(r"## \[(\d+\.\d+\.\d+)\]", content)
        if match:
            return match.group(1)
    return "0.0.0"

def bump_version(version, type="patch"):
    major, minor, patch = map(int, version.split("."))
    if type == "major":
        return f"{major + 1}.0.0"
    elif type == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"

def analyze_changes(files):
    areas = []
    for f in files:
        if f.startswith("frontend/"):
            areas.append("frontend")
        elif f.startswith("backend/"):
            areas.append("backend")
        elif f.startswith("tests/"):
            areas.append("tests")
        else:
            areas.append("other")
    
    areas = sorted(list(set(areas)))
    return f"Updated {', '.join(areas)}: {', '.join(files[:3])}" + ("..." if len(files) > 3 else "")

def update_changelog(new_version, entry):
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_section = f"## [{new_version}] - {date_str}\n\n### Changed\n- {entry}\n\n"
    
    with open(CHANGELOG_PATH, "r") as f:
        content = f.read()
    
    # Prepend the new section after any header (if exists) or at the top
    # For Keep a Changelog, it usually follows the title
    if content.startswith("# Changelog"):
        # Insert after the first line (title) and any description
        lines = content.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("## "):
                insert_idx = i
                break
        
        if insert_idx == 0: # No previous versions found
            new_content = "\n".join(lines[:1]) + "\n\n" + new_section + "\n".join(lines[1:])
        else:
            new_content = "\n".join(lines[:insert_idx]) + "\n" + new_section + "\n".join(lines[insert_idx:])
    else:
        new_content = new_section + content
        
    with open(CHANGELOG_PATH, "w") as f:
        f.write(new_content)

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", action="store_true", help="Accept the proposed entry without prompting")
    args = parser.parse_args()

    staged_files = get_staged_files()
    if not staged_files:
        print("No staged changes found.")
        return

    # Filter out CHANGELOG.md itself to avoid loops
    staged_files = [f for f in staged_files if f != CHANGELOG_PATH]
    if not staged_files:
        return

    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    suggested_entry = analyze_changes(staged_files)
    
    bump_type = "patch"
    if any("view" in f.lower() or "component" in f.lower() for f in staged_files):
        bump_type = "minor"
        
    new_version = bump_version(current_version, bump_type)
    
    print("\n--- Proposed Changelog Entry ---")
    print(f"Version: {new_version} ({bump_type})")
    print(f"Entry: {suggested_entry}")
    print("--------------------------------\n")
    
    if args.yes:
        print("Accepted automatically (--yes flag).")
        update_changelog(new_version, suggested_entry)
        subprocess.run(["git", "add", CHANGELOG_PATH], check=True)
        print(f"✅ CHANGELOG.md updated and staged to version {new_version}")
        return

    # Try to get interactive input
    try:
        # Check if stdin is a TTY
        if not sys.stdin.isatty():
            # If not a TTY, we might be in a git hook. Try to open /dev/tty
            try:
                tty = open("/dev/tty", "r")
                sys.stdin = tty
            except (OSError, IOError):
                # If we can't open /dev/tty, we skip
                print("Could not open /dev/tty for interactive input. Skipping.")
                return
        
        response = input("Accept this entry? [Y/n/edit]: ").strip().lower()
        
        if response == "edit" or response == "e":
            new_version = input(f"Enter version [{new_version}]: ").strip() or new_version
            suggested_entry = input(f"Enter entry: ").strip() or suggested_entry
        elif response == "n":
            print("Changelog update cancelled.")
            return
        elif response == "" or response == "y" or response == "yes":
            pass # Use suggested values
        else:
            print(f"Unknown response: {response}. Cancelled.")
            return
        
        update_changelog(new_version, suggested_entry)
        subprocess.run(["git", "add", CHANGELOG_PATH], check=True)
        print(f"✅ CHANGELOG.md updated and staged to version {new_version}")
            
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended unexpectedly. Skipping changelog update.")
    except Exception as e:
        print(f"Error during changelog update: {e}")

if __name__ == "__main__":
    main()
