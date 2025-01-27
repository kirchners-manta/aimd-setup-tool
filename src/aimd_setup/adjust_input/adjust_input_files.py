# Part of the AIMD setup tool

"""
Functions to adjust input files for the AIMD setup tool.
"""

#############################################

from __future__ import annotations

import os
from typing import Any


def cp_runscript(
    data: dict[str, Any], template_dir: str, project_dir: str, bqb_count: int = 0
) -> None:
    """Copy the runscript to the project directory, and edit the runscript according to user input

    Parameters
    ----------
    data : dict
        dictionary containing the data for the calculation
    template_dir : str
        path to the directory containing the template files
    project_dir : str
        path to the directory where the files should be copied to
    bqb_count : int
        Counter for the number of BQB calculations
    """

    # copy the runscript
    os.system(
        "cp " + template_dir + "/../runscripts/" + data["runscript"] + " " + project_dir
    )

    # open the file
    with open(data["runscript"], "r") as f:

        lines = f.readlines()
        for i, line in enumerate(lines):
            if "PROJECT_NAME" in line:
                if bqb_count > 0:
                    lines[i] = line.replace(
                        "PROJECT_NAME", data["project"] + f"_{bqb_count+1:02d}"
                    )
                else:
                    lines[i] = line.replace("PROJECT_NAME", data["project"])
            if "Part of the AIMD setup tool" in line:
                lines[i] = line.replace(
                    "Part of the AIMD setup tool", "Created by the AIMD setup tool"
                )
            if "N_CPU" in line:
                lines[i] = line.replace("N_CPU", str(data["cpu"]))

        jobs = ["geoopt", "eq", "relax", "prod", "bqb", "energy"]

        for i, job in enumerate(jobs):
            if data["joblist"][i] == True:
                lines.insert(-1, f"srun cp2k.psmp {job}.inp >{job}.out\n")

        # remove the job submission lines for jobs that are not requested

        with open(data["runscript"], "w") as g:
            g.writelines(lines)
