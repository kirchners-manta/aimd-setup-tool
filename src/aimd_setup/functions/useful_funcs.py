"""
Useful helper functions used for the AIMD setup.
"""

from __future__ import annotations

from pathlib import Path
import sys
import os

def getFileList(path: str, regex: str) -> list:
    """Get a list of files in a directory.

    Parameters
    ----------
    path : str
        path to the directory where the files are located
    regex : str
        regular expression to filter the files

    Returns
    -------
    list
        list of posix paths to the files
    """
    filelist = []
    for file in sorted(Path(path).rglob(regex)):
        filelist.append(file)

    if len(filelist) == 0:
        sys.exit("No '*data' files found.")

    return filelist

def make_project_dir(project_directory: str, overwrite: bool) -> None:
    """Create a project directory. Check if the project directory exists; if yes, ask if it should be overwritten; if no, create it

    Parameters
    ----------
    project_directory : str
        path to the project directory
    overwrite : bool
        if True, overwrite existing project directory
    """

    if os.path.isdir(project_directory) and not overwrite:
        print(
            "Project directory '"
            + project_directory
            + "' already exists. Shall is be overwritten? [y/n]"
        )
        answer = input()
        if answer in ["y", "Y", "j", "J"]:
            os.system("rm -rf " + project_directory)
            print("Overwriting old project directory '" + project_directory + "'.\n")
            os.system("mkdir " + project_directory)
        else:
            sys.exit("Project directory not overwritten. Exiting.\n")
    elif os.path.isdir(project_directory) and overwrite:
        os.system("rm -rf " + project_directory)
        print("Overwriting old project directory '" + project_directory + "'.\n")
        os.system("mkdir " + project_directory)
    else:
        print("Creating new project directory '" + project_directory + "'.\n")
        os.system("mkdir " + project_directory)