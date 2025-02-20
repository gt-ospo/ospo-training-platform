import subprocess
import json
import os

def is_nbgrader_running():
    """Checks if nbgrader is running in validation or auto-grading mode."""
    current_dir = os.getcwd()
    
    # Check if student is manually validating or autograder is running
    if os.getenv("NBGRADER_VALIDATING") == "1" or "autograded" in current_dir:
        return True

    return False

def save_git_state(filename, test_name):
    """Saves Git state only if nbgrader is NOT running."""
    
    if is_nbgrader_running():
        return f"Skipped saving Git state for {test_name} (nbgrader execution)."
        
    cwd = os.getcwd()
    hidden_dir = os.path.join(cwd, "../.git_states")
    os.makedirs(hidden_dir, exist_ok=True)
    filename = os.path.join(hidden_dir, filename)

    git_state = {
        "commit": subprocess.getoutput("git rev-parse HEAD"),
        "branch": subprocess.getoutput("git rev-parse --abbrev-ref HEAD"),
        "staged_files": subprocess.getoutput("git diff --name-only --cached"),
        "unstaged_files": subprocess.getoutput("git diff --name-only"),
        "untracked_files": subprocess.getoutput("git ls-files --others --exclude-standard"),
        "last_5_commits": subprocess.getoutput("git log --oneline -5"),
        "diff_summary": subprocess.getoutput("git diff --stat")
    }

    remote_branch = subprocess.getoutput("git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null")
    remote_commit = subprocess.getoutput("git log --oneline -1 origin/main 2>/dev/null")

    # Store remote commit info (if available)
    if remote_branch and remote_commit:
        git_state["remote_branch"] = remote_branch
        git_state["remote_commit"] = remote_commit.split(" ")[0] # The most recent remote commit

    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:  # Ensure file isn't empty
            with open(filename, "r") as f:
                all_states = json.load(f)
        else:
            all_states = {}
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        all_states = {}

    all_states[test_name] = git_state

    with open(filename, "w") as f:
        json.dump(all_states, f, indent=4)

    return f"Saved git state for {test_name}."

def load_git_state(filename, test_name):
    """Loads stored git state for a specific test in a given file."""
    cwd = os.getcwd()
    hidden_dir = os.path.join(cwd, "../.git_states")
    filename = os.path.join(hidden_dir, filename)

    if not os.path.exists(filename):
        raise ValueError(f"No Git state file found for this section!")

    with open(filename, "r") as f:
        all_states = json.load(f)

    if test_name not in all_states:
        raise ValueError(f"No Git state found for test '{test_name}'!")

    return all_states[test_name]