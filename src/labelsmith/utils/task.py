import appdirs
import os
from pathlib import Path

# Initialize application-specific directory paths
app_name = "Labelsmith"
app_author = "kosmolebryce"

# Determine application-specific directories
app_data_dir = appdirs.user_data_dir(app_name, app_author)
app_config_dir = appdirs.user_config_dir(app_name, app_author)
app_cache_dir = appdirs.user_cache_dir(app_name, app_author)

# Ensure directories exist
Path(app_data_dir).mkdir(parents=True, exist_ok=True)
Path(app_config_dir).mkdir(parents=True, exist_ok=True)
Path(app_cache_dir).mkdir(parents=True, exist_ok=True)

# Global variable
corpus = []

# Helper Functions
def print_tasks():
    global corpus
    task_data_string = ""
    for enum, task_dict in enumerate(corpus, start=1):
        for key, task_data in task_dict.items():
            permalink = task_data["permalink"]
            rid1 = task_data["rid1"]
            rid2 = task_data["rid2"]
            rank = task_data["rank"]
            justification = task_data["justification"]
            task_data_string += f"""
{enum}. `{key}`

[Permalink]
{permalink}

[Response IDs]
1. `{rid1}`
2. `{rid2}`

[Rank]
{rank}

[Justification]
{justification}

"""
            
    print(task_data_string)
    return task_data_string


def scan(directory=app_data_dir):
    try:
        entries = [entry.name for entry in os.scandir(directory) if entry.name.endswith(".md")]
        return entries
    except FileNotFoundError:
        print(f"The directory {directory} does not exist.")
        return []
    except PermissionError:
        print(f"Permission denied for accessing the directory {directory}.")
        return []

def extract_numeric_part(file_name):
    return int(file_name.split('.')[0])

def get_highest_order(prefix_list):
    if not prefix_list:
        return None  # Handle the case when no .md files are found
    return max(prefix_list)

class Task:
    def __init__(
        self,
        tid=None,
        permalink=None,
        rid1=None,
        rid2=None,
        rank=None,
        justification=None,
        task_dict={}):
        self.tid = tid
        self.permalink = permalink
        self.rid1 = rid1
        self.rid2 = rid2
        self.rank = rank
        self.justification = justification
        self.task_dict = task_dict
        self.attempt()
        global corpus
        corpus.append(self.task_dict)

    def attempt(self) -> dict:
        self.tid = input("Enter the task ID: ")
        self.permalink = input("Enter the SRT permalink: ")
        self.rid1 = input("Enter the numerical ID for Response #1: ")
        self.rid2 = input("Enter the numerical ID for Response #2: ")
        self.rank = input("Enter your rank for the provided model response pair:\n")
        self.justification = input("Enter your justification for the previous entry:\n")
        
        self.task_dict = {
            self.tid: {
                "permalink": self.permalink,
                "rid1": self.rid1,
                "rid2": self.rid2,
                "rank": self.rank,
                "justification": self.justification,
                }
            }
                
        return (
            self.tid, self.permalink, self.rid1, self.rid2, self.rank,
            self.justification, self.task_dict
            )

def main():
    response = "y"
    try:
        while response.lower() == "y":
            task = Task()
            response = input("Add another task? (y/n)\n")
        response = input("Write task data to markdown file? (y/n)\n")
        if response.lower() == "y":
            # Scan the directory for .md files
            entries = scan()
            # Extract the numeric parts from the filenames
            prefixes = [extract_numeric_part(e) for e in entries]
            # Get the highest numeric prefix
            highest_order = get_highest_order(prefixes)

            if highest_order is not None:
                new_filename = f"{(highest_order + 1):04d}.md"
            else:
                new_filename = "0001.md"

            text_header = f"""
# `{new_filename}`

----
"""
            text_content = print_tasks()
            text = f"""
{text_header}
{text_content}
"""

            # Write the entire text to the file
            with open(f"{app_data_dir}/{new_filename}", "w") as f:
                f.write(text)

            
        else:
            print("Skipped data file creation.")
            print()
            print_tasks()
    except KeyboardInterrupt:
        print(f"\n\nAborted!\n\n")


if __name__ == "__main__":
    main()
