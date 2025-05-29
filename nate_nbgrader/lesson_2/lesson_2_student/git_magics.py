import subprocess
from git_state_manager import save_git_state as save_git_state_func, load_git_state

def save_git_state_magic(line, cell):
    args = line.strip().split()
    if len(args) != 2:
        print("Usage: %%save_git_state <filename.json> <test_name>")
        return

    filename, test_name = args

    for command in cell.strip().splitlines():
        if command.strip() and command.strip() not in ["# YOUR CODE HERE", "### BEGIN SOLUTION", "### END SOLUTION"]:
            print(f"$ {command}")
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)

    print(save_git_state_func(filename, test_name))

def load_ipython_extension(ipython):
    ipython.register_magic_function(save_git_state_magic, "cell", "save_git_state")