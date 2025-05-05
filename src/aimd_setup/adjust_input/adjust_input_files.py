# Part of the AIMD setup tool

"""
Functions to adjust input files for the AIMD setup tool.
"""

#############################################

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


def cp_runscript(
    data: dict[str, Any], template_dir: Path, project_dir: Path, bqb_count: int = -1
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

    # dictionary with the cp2k version strings
    cp2k_version_strings = {
        "noctua2": {
            "2023.1": "chem/CP2K/2023.1-foss-2022b-gcc-openmpi-openblas",
            "2025.1": "chem/CP2K/2025.1-foss-2023b-gcc-openmpi-openblas",
        },
        "bonna": {},
        "marvin": {},
    }

    # copy the runscript
    shutil.copy(
        (template_dir / "../runscripts" / data["runscript"]).resolve(),
        project_dir.resolve() / data["runscript"],
    )

    # open the file
    with open(data["runscript"]) as f:

        lines = f.readlines()
        for i, line in enumerate(lines):
            if "PROJECT_NAME" in line:
                if bqb_count >= 0:
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
                # define cpus per node
                if data["queue"] == "bonna":
                    cpuspernode = 32
                elif data["queue"] == "noctua2":
                    cpuspernode = 128

                if data["cpu"] % cpuspernode == 0:
                    nodes = data["cpu"] // cpuspernode
                else:
                    nodes = data["cpu"] // cpuspernode + 1
                if data["cpu"] % nodes != 0:
                    raise ValueError(
                        f"Number of CPUs ({data['cpu']}) must be divisible by the number of nodes ({nodes})"
                    )

                data["cpu"] = data["cpu"] // nodes

                lines[i] = line.replace("N_CPU", str(data["cpu"]))

            if "N_NODES" in line:
                lines[i] = line.replace("N_NODES", str(nodes))

            if "VERSION_CP2K" in line:
                lines[i] = line.replace(
                    "VERSION_CP2K",
                    cp2k_version_strings[data["queue"]][data["cp2k_version"]],
                )

        jobs = ["geoopt", "eq", "relax", "prod", "bqb", "energy"]

        for i, job in enumerate(jobs):
            if data["joblist"][i] == True:
                if data["queue"] == "noctua2":
                    lines.insert(len(lines), f"srun cp2k.psmp {job}.inp >{job}.out\n")
                elif data["queue"] == "bonna":
                    lines.insert(
                        len(lines),
                        f"mpirun /home/chemie/install_cp2k/cp2k-2024.3/exe/local/cp2k.psmp {job}.inp >{job}_output\n",
                    )

        # remove the job submission lines for jobs that are not requested

        with open(data["runscript"], "w") as g:
            g.writelines(lines)  #
