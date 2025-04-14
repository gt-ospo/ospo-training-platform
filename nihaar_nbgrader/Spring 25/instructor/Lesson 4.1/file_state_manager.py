import os
import shutil
import json

repo_path = ""
def save_state(files, lesson, checkpoint):
    state_folder = os.path.join(repo_path, f"lesson_{lesson}_checkpoint_{checkpoint}")
    if os.path.exists(state_folder):
        shutil.rmtree(state_folder)
    os.makedirs(state_folder)
    os.getcwd()
    os.listdir()
    
    metadata = {
        "lesson": lesson,
        "checkpoint": checkpoint,
        "files": files
    }

    # copies files
    for file in files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(state_folder, os.path.basename(file)))

    with open(os.path.join(state_folder, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Saved state: Lesson {lesson}, Checkpoint {checkpoint}")


def load_state(lesson, checkpoint):
    state_folder = os.path.join(repo_path, f"lesson_{lesson}_checkpoint_{checkpoint}")
    metadata_file = os.path.join(state_folder, "metadata.json")

    if not os.path.exists(metadata_file):
        print(f"No saved state found for Lesson {lesson}, Checkpoint {checkpoint}")
        return False
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    # restore
    for file in metadata["files"]:
        saved_file = os.path.join(state_folder, os.path.basename(file))
        if os.path.exists(saved_file):
            shutil.copy2(saved_file, file) 
            print(f"Restored: {file}")
        else:
            print(f"Warning: {saved_file} not found in saved state.")

    print(f"Restored state: Lesson {lesson}, Checkpoint {checkpoint}")
    return True