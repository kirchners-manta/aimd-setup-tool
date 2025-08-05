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
    data: dict[str, Any],
    template_dir: Path,
    project_dir: Path,
    bqb_count: int = -1,
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
        "marvin": {
            "2024.3": "/opt/software/ag_mctc_kirchner/cp2k-2024.3",
            "2025.2": "/opt/software/ag_mctc_kirchner/cp2k-2025.2",
        },
        "berta2": {
            "2024.3": "/software/cluster-2/cp2k-2024.3_berta",
        },
        "iris2": {
            "2024.3": "/software/cluster-2/cp2k-2024.3_iris",
        },
        "hedy2": {
            "2024.3": "/software/cluster-2/cp2k-2024.3_iris",
        },
    }

    # check if runscript for the requested queue exists
    if data["cp2k_version"] not in cp2k_version_strings[data["queue"]]:
        raise ValueError(
            f"CP2K version {data['cp2k_version']} not available for queue {data['queue']}. "
            f"Available versions: {', '.join(cp2k_version_strings[data['queue']].keys())}"
        )

    # copy the runscript
    shutil.copy(
        (template_dir / "../runscripts" / data["runscript"]).resolve(),
        project_dir.resolve() / data["runscript"],
    )

    # open the file
    with open(data["runscript"]) as f:

        lines = f.readlines()
        for i, line in enumerate(lines):
            # find line to insert the software execution command
            if "# execute job" in line:
                ijob = i

            if "PROJECT_NAME" in line:
                if bqb_count >= 0:
                    lines[i] = line.replace(
                        "PROJECT_NAME", data["project"] + f"_{bqb_count+1:02d}"
                    )
                else:
                    lines[i] = line.replace("PROJECT_NAME", data["project"])
            if "Part of the AIMD setup tool" in line:
                lines[i] = line.replace(
                    "Part of the AIMD setup tool",
                    "Created by the AIMD setup tool",
                )
            if "N_CPU" in line:
                # define cpus per node
                if data["queue"] == "bonna":
                    cpuspernode = 32
                elif data["queue"] == "noctua2":
                    cpuspernode = 128
                elif data["queue"] == "marvin":
                    cpuspernode = 96
                elif data["queue"] == "berta2":
                    cpuspernode = 32
                elif data["queue"] == "iris2":
                    cpuspernode = 64
                elif data["queue"] == "hedy2":
                    cpuspernode = 64

                if data["cpu"] % cpuspernode == 0:
                    nodes = data["cpu"] // cpuspernode
                else:
                    nodes = data["cpu"] // cpuspernode + 1
                if data["cpu"] % nodes != 0:
                    raise ValueError(
                        f"Number of CPUs ({data['cpu']}) must be divisible by the number of nodes ({nodes})"
                    )

                data["cpu"] = data["cpu"] // nodes

                if nodes > 1 and data["queue"] in ["berta2", "iris2", "hedy2"]:
                    raise ValueError(
                        f"Number of nodes ({nodes}) must be 1 for {data['queue']} queue"
                    )

                lines[i] = line.replace("N_CPU", str(data["cpu"]))

            if "N_NODES" in line:
                lines[i] = line.replace("N_NODES", str(nodes))

            if "VERSION_CP2K" in line:
                lines[i] = line.replace(
                    "VERSION_CP2K",
                    cp2k_version_strings[data["queue"]][data["cp2k_version"]],
                )

        jobs = ["geoopt", "eq", "relax", "prod", "bqb", "energy"]

        for j, job in enumerate(jobs):
            if data["joblist"][j] == True:
                if data["queue"] == "noctua2":
                    lines.insert(
                        ijob + j, f"srun cp2k.psmp {job}.inp >{job}.out\n"
                    )
                elif data["queue"] in ["bonna", "berta2", "iris2", "hedy2"]:
                    lines.insert(
                        ijob + j,
                        f"mpirun {cp2k_version_strings[data['queue']][data['cp2k_version']]}/cp2k.psmp {job}.inp >{job}.out\n",
                    )
                elif data["queue"] == "marvin":
                    lines.insert(
                        ijob + j,
                        f"mpirun {cp2k_version_strings[data['queue']][data['cp2k_version']]}/exe/local/cp2k.psmp {job}.inp >{job}.out\n",
                    )

        with open(data["runscript"], "w") as g:
            g.writelines(lines)
