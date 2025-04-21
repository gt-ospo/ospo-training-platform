# Internal Developer: Git Course (nbgrader + Git Magics)

This repository and configuration power the `git_course_test` course hosted on our shared JupyterHub environment. It integrates `nbgrader` with custom Git magic commands for teaching Git workflows interactively.

---

## Setup Overview

### Shared Folder Structure (on JupyterHub)
- `/shared/nbgrader/courses/git_course_test/`: Contains the course materials and global config for the course.
- `/shared/nbgrader/exchange/git_course_test/`: Exchange directory for assignment distribution to students in the `outbound` folder, and where students submit their assignments that go into the `inbound` folder.

---

## nbgrader Configuration

### Shared Server Global Config (`/shared/nbgrader/courses/git_course_test/nbgrader_config.py`)
```python
c.CourseDirectory.course_id = "git_course_test"
c.IncludeHeaderFooter.header = "source/header.ipynb"
c.CourseDirectory.root = '/shared/nbgrader/courses/git_course_test'
```
This config sets up the course in a shared area so that multiple instructors can access material, and students can fetch, submit, and retrieve feedback for their assignments.

### Instructor Account's Personal Server Config (`/home/{user_id}/nbgrader_config.py`)
```python
c.CourseDirectory.course_id = "git_course_test"
c.CourseDirectory.root = '/shared/nbgrader/courses/git_course_test'
c.NbGrader.db_url = 'sqlite:////shared/nbgrader/courses/git_course_test/gradebook.db'
c.IncludeHeaderFooter.header = "source/header.ipynb"
```
This config allows instructors to access course materials and the formgrader. Processes such as generating student versions of assignments, as well as releasing, collecting, and grading assignments from the instructor's server require this config change.


----------------------------------------------------

# Git Course Python Magics

This document explains the custom **Jupyter cell magics** developed for use in the `git_course_test` nbgrader course on JupyterHub. These magics are used to **capture Git repository states** during notebook execution, while avoiding interference with the nbgrader autograder.

--------------------------------------

## File Overview
`git_magics.py`: Registers the `%save_git_state` cell magic

---

## Magic: `%%save_git_state`

### Purpose
This magic captures the state of the student's Git repository during a specific exercise. It helps instructors verify that students used Git commands correctly. In addition it cleans up the code cells so users don't need to see unnecessary code for saving git states, as well as remove the need for extra syntax for the user to enter in commands. They now can enter in commands just as they would in the terminal.

### Usage

Add this line of code to the top of your notebook to import the magic:
```python
%load_ext git_magics
```

Then, in a notebook cell:

```python
%%save_git_state filename.json test_name
git add my_file.py
git commit -m "finished the task"
```

### Arguments
- `filename.json`: The filename to store Git states for the given sublesson. (saved inside `.git_states/`).
- `test_name`: A label representing the test name for the given sublesson.

---

## How Does It Work?

1. Parses the `filename.json`, and `test_name`.
2. Runs each command line by line, ignoring any boilerplate code such as `# YOUR CODE HERE`.
3. Saves the current git state to the `.git_states/` folder so that tests can retrieve this information.