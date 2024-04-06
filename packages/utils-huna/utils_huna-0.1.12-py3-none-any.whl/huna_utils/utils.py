import os
import sys
import git


def git_path():
    repo = git.Repo('.', search_parent_directories=True)
    module_path = repo.working_tree_dir
    sys.path.append(module_path)
    os.environ['MODULE_PATH'] = module_path
    
    return module_path


def file_path(file_name, extensions):
    folders_with_csv_parquet = []

    for root, dirs, files in os.walk(master_folder):
        if any(file.endswith(tuple(extensions)) for file in files):
            return root, 
        
def current_path(level_path = -3):
    path_complete = os.getcwd()
    folder = path_complete.split("/")

    last_folder = folder[level_path:]
    short_path = "/".join(last_folder)
    
    return short_path