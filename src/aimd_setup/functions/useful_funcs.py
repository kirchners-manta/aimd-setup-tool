"""
Useful helper functions used for the AIMD setup.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def getFileList(path: str, regex: str) -> list[Path]:
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


def make_project_dir(project_directory: Path, overwrite: bool) -> None:
    """Create a project directory. Check if the project directory exists; if yes, ask if it should be overwritten; if no, create it

    Parameters
    ----------
    project_directory : str
        path to the project directory
    overwrite : bool
        if True, overwrite existing project directory
    """

    if project_directory.exists():
        if not overwrite:
            print(
                f"Project directory '{project_directory}' already exists. Shall it be overwritten? [y/n]"
            )
            answer = input().strip().lower()
            if answer not in ["y", "j"]:
                sys.exit("Project directory not overwritten. Exiting.")

        # remove the existing directory
        shutil.rmtree(project_directory)
        print(f"Overwriting existing project directory.")

    # create the project directory
    else:
        print(f"Creating new project directory '{project_directory}'.")

    project_directory.mkdir(parents=True, exist_ok=True)
