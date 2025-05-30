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
        
    module_dir = os.path.dirname(os.path.abspath(__file__))
    hidden_dir = os.path.join(module_dir, ".git_states")
    
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
    module_dir = os.path.dirname(os.path.abspath(__file__))
    hidden_dir = os.path.join(module_dir, ".git_states")

    filename = os.path.join(hidden_dir, filename)

    if not os.path.exists(filename):
        raise ValueError(f"No Git state file found for this section!")

    with open(filename, "r") as f:
        all_states = json.load(f)

    if test_name not in all_states:
        raise ValueError(f"No Git state found for test '{test_name}'!")

    return all_states[test_name]


def save_git_checkpoint(sublesson_name):
    """Saves a full checkpoint of the Git repository state at the beginning of a sublesson."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    hidden_dir = os.path.join(module_dir, ".git_states")
    os.makedirs(hidden_dir, exist_ok=True)

    filename = os.path.join(hidden_dir, f"{sublesson_name}_checkpoint.json")

    # Save each branch and its corresponding commit
    branches = subprocess.getoutput("git branch --format='%(refname:short)'").split("\n")
    branch_commits = {}
    for branch in branches:
        commit = subprocess.getoutput(f"git rev-parse {branch}")
        branch_commits[branch] = commit

    git_state = {
        "branches": branch_commits,
        "current_branch": subprocess.getoutput("git rev-parse --abbrev-ref HEAD"),
        "staged_files": subprocess.getoutput("git diff --name-only --cached").split("\n"),
        "unstaged_files": subprocess.getoutput("git diff --name-only").split("\n"),
        "untracked_files": subprocess.getoutput("git ls-files --others --exclude-standard").split("\n"),
        "diff_summary": subprocess.getoutput("git diff --stat"),
        "remote_branch": subprocess.getoutput("git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null"),
        "remote_commit": subprocess.getoutput("git log --oneline -1 origin/main 2>/dev/null")
    }

    with open(filename, "w") as f:
        json.dump(git_state, f, indent=4)

    return f"Saved checkpoint for '{sublesson_name}'."


def restore_git_checkpoint(sublesson_name):
    """Restores the Git repository state from a saved checkpoint."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    hidden_dir = os.path.join(module_dir, ".git_states")
    filename = os.path.join(hidden_dir, f"{sublesson_name}_checkpoint.json")

    if not os.path.exists(filename):
        raise ValueError(f"No checkpoint found for '{sublesson_name}'.")

    with open(filename, "r") as f:
        checkpoint = json.load(f)

    print(f"Restoring Git checkpoint for '{sublesson_name}'...")

    # Step 1: Clean working directory (remove all local changes, including untracked files)
    subprocess.run(["git", "reset", "--hard"], check=True)
    subprocess.run(["git", "clean", "-fd"], check=True)

    existing_branches = subprocess.getoutput("git branch --format='%(refname:short)'").split("\n")
    checkpoint_branches = checkpoint["branches"]

    # Step 2: Restore branches to exact commits
    for branch, commit in checkpoint_branches.items():
        if branch == checkpoint["current_branch"]:
            continue
        elif branch in existing_branches:
            subprocess.run(["git", "branch", "-f", branch, commit], check=True)
        else:
            subprocess.run(["git", "branch", branch, commit], check=True)
        print(f"Set branch '{branch}' to {commit}")

    # Step 3: Checkout the checkpoint branch and reset to saved commit
    subprocess.run(["git", "checkout", checkpoint["current_branch"]], check=True)
    subprocess.run(["git", "reset", "--hard", checkpoint_branches[checkpoint["current_branch"]]], check=True)
    print(f"Checked out and reset to branch '{checkpoint['current_branch']}'")

    # Step 4: Now delete any branches not in the checkpoint
    updated_branches = subprocess.getoutput("git branch --format='%(refname:short)'").split("\n")
    for branch in updated_branches:
        if branch not in checkpoint_branches:
            subprocess.run(["git", "branch", "-D", branch], check=True)
            print(f"Removed branch: {branch}")

    return f"Restored Git checkpoint for '{sublesson_name}'."

