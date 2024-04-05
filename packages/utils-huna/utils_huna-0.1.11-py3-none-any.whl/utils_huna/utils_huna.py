import os
import sys
import git


def git_path():
    repo = git.Repo('.', search_parent_directories=True)
    module_path = repo.working_tree_dir
    return module_path


def folder_path(master_folder, extensions):
    folders_with_csv_parquet = []

    for root, dirs, files in os.walk(master_folder):
        if any(file.endswith(tuple(extensions)) for file in files):
            return root