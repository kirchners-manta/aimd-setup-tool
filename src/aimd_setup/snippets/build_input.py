"""
Script to build input files for CP2K simulations, based on pre-defined input snippets.
"""

from __future__ import annotations

import copy
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def get_default_sections() -> dict[str, Any]:
    """Get the default sections for the CP2K input file.

    Returns
    -------
    dict[str, Any]
        Dictionary containing all implemented sections for the CP2K input files.
        By default, some sections are disabled.
    """

    sections = {
        "global": {
            "add": True,
            "header": "header.inp",
            "keywords": "keywords.inp",
        },
        "motion": {
            "add": True,
            "header": "header.inp",
            "keywords": "keywords.inp",
            "geo_opt": {
                "add": False,
                "header": "header.inp",
                "keywords": "keywords.inp",
            },
            "md": {
                "add": True,
                "header": "header.inp",
                "keywords": "keywords.inp",
                "thermostat": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "nose": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "reftraj": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
            },
            "print": {
                "add": True,
                "header": "header.inp",
                "keywords": "keywords.inp",
                "cell": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "each": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "forces": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "each": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "restart": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "each": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "restart_history": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "each": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "trajectory": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "each": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "velocities": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "each": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
            },
        },
        "force_eval": {
            "add": True,
            "header": "header.inp",
            "keywords": "keywords.inp",
            "dft": {
                "add": True,
                "header": "header.inp",
                "keywords": "keywords.inp",
                "localize": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "print": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                        "wannier_centers": {
                            "add": True,
                            "header": "header.inp",
                            "keywords": "keywords.inp",
                            "each": {
                                "add": True,
                                "header": "header.inp",
                                "keywords": "keywords.inp",
                            },
                        },
                    },
                },
                "mgrid": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
                "periodic_efield": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
                "poisson": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
                "print": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "e_density_bqb": {
                        "add": False,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                        "each": {
                            "add": True,
                            "header": "header.inp",
                            "keywords": "keywords.inp",
                        },
                    },
                    "e_density_cube": {
                        "add": False,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                        "each": {
                            "add": True,
                            "header": "header.inp",
                            "keywords": "keywords.inp",
                        },
                    },
                    "voronoi": {
                        "add": False,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                        "each": {
                            "add": True,
                            "header": "header.inp",
                            "keywords": "keywords.inp",
                        },
                    },
                },
                "qs": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "xtb": {
                        "add": False,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "scf": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "ot": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                    "outer_scf": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
                "xc": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "vdw_potential": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                        "pair_potential": {
                            "add": True,
                            "header": "header.inp",
                            "keywords": "keywords.inp",
                        },
                    },
                    "xc_functional": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                        "blyp": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "bp": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "pade": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "pbe": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "pbe0": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "r2scan": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "revpbe": {
                            "add": False,
                            "header": "header.inp",
                        },
                        "scan": {
                            "add": False,
                            "header": "header.inp",
                        },
                    },
                    "xc_grid": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                },
            },
            "subsys": {
                "add": True,
                "header": "header.inp",
                "keywords": "keywords.inp",
                "cell": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
                "kind_h": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_d": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_li": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_b": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_c": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_n": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_o": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_f": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_na": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_mg": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_p": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_s": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_cl": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_k": {
                    "add": False,
                    "header": "header.inp",
                },
                "kind_ti": {
                    "add": False,
                    "header": "header.inp",
                    "dft_plus_u": {
                        "add": False,
                        "header": "header.inp",
                    },
                },
                "kind_fe": {
                    "add": False,
                    "header": "header.inp",
                    "dft_plus_u": {
                        "add": False,
                        "header": "header.inp",
                    },
                },
                "kind_co": {
                    "add": False,
                    "header": "header.inp",
                    "dft_plus_u": {
                        "add": False,
                        "header": "header.inp",
                    },
                },
                "kind_zn": {
                    "add": False,
                    "header": "header.inp",
                    "dft_plus_u": {
                        "add": False,
                        "header": "header.inp",
                    },
                },
                "kind_br": {
                    "add": False,
                    "header": "header.inp",
                },
                "topology": {
                    "add": True,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
                "velocity": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                },
            },
        },
        "ext_restart": {
            "add": False,
            "header": "header.inp",
            "keywords": "keywords.inp",
        },
    }

    return sections


def print_structure(
    sections: dict[str, Any],
    prefix: str = "",
) -> None:
    """Print the structure of a dictionary containing the sections for the CP2K input file. A section is printed if the key "add" is set to True.
    This is a recursive function.

    Parameters
    ----------
    sections : dict[str, Any]
        Dictionary containing the sections for the CP2K input file.
    prefix : str, optional
        For printing, by default "". Exists because of the recursive nature of the function. Do not set manually.
    """
    for section, content in sections.items():
        if isinstance(content, dict) and content.get("add"):
            print(f"{prefix}{section}")
            print_structure(content, prefix=f"{prefix}{section}: ")


def build_file(
    lines: list[str],
    sections: dict[str, Any],
    prefix: str = "",
) -> list[str]:
    """Build a CP2k input file based on a dictionary containing the sections for the CP2K input file.
    A section is added if the key "add" is set to True.
    This is a recursive function.

    Parameters
    ----------
    lines : List[str]
        List containing the lines of the CP2K input file.
    sections : dict[str, Any]
        Dictionary containing the sections for the CP2K input file.
    prefix : str, optional
        For navigating, by default "". Exists because of the recursive nature of the function. Do not set manually.
    """

    # where the snippets are located
    directory = Path(__file__).parent
    tab = "  "
    # iterate through dictionary
    for section, content in sections.items():
        if isinstance(content, dict) and content.get("add"):

            # current depth determines the position of the lines
            current_depth = f"{prefix}{section}".count("/")

            # read header
            if "header" in content:
                with open(
                    directory / prefix / section / content["header"],
                    encoding="utf-8",
                ) as f:
                    # get a list of lines that should be added
                    lines_to_add = f.read().splitlines()
                    # add at the second to last position
                    for i, line in enumerate(lines_to_add):
                        # remove comments and empty lines
                        if len(line.split("#")[0].rstrip()) != 0:
                            # if the current depth is 0, add at the last position
                            if current_depth == 0:
                                lines.insert(-1, line.split("#")[0].rstrip())
                            # else, add at the second to last position
                            else:
                                lines.insert(
                                    len(lines) - 1 - current_depth,
                                    f"{tab * current_depth}{line.split('#')[0].rstrip()}",
                                )

            # read keywords
            if "keywords" in content:
                with open(
                    directory / prefix / section / content["keywords"],
                    encoding="utf-8",
                ) as f:
                    # get a list of lines that should be added
                    lines_to_add = f.read().splitlines()
                    # add at the second to last position
                    for i, line in enumerate(lines_to_add):
                        if len(line.split("#")[0].rstrip()) != 0:
                            lines.insert(
                                len(lines) - 2 - current_depth,
                                f"{tab * (current_depth + 1)}{line.split('#')[0].rstrip()}",
                            )

            # recursive call
            lines = build_file(
                lines,
                content,
                prefix=f"{prefix}{section}/",
            )

    return lines


def get_atom_types(coord_file: str) -> list[str]:
    """Read the atom types from a coordinate file (assumed to be in xyz format)

    Parameters
    ----------
    coord_file : str
        Path to the coordinate file in xyz format.

    Returns
    -------
    list[str]
        List containing the atom types.
    """

    with open(coord_file, encoding="utf-8") as f:
        lines = f.readlines()
        atom_types = [line.split()[0] for line in lines[2:]]

    # remove duplicates
    atom_types = list(set(atom_types))

    return atom_types


def generate_input_files(data: dict[str, Any], bqb_count: int = 0) -> None:
    """Generate input files for CP2K simulations.

    Parameters
    ----------
    data : dict[str, Any]
        Dictionary containing the input parameters specified by the user.
    bqb_count : int, optional
        Counter for the bqb files, by default 0. Used to name the bqb files.
        Not used for the other input files.

    Important:
    The dictionary must contain the following key:
    joblist :
        List of boolean values indicating if the input files should be generated.
        Entries correspond to the following jobs:
        - geometry optimization
        - equilibration
        - relaxation
        - production
        - bqb file calculation
        - single point energy calculation
    """

    # get default sections
    sections = get_default_sections()

    # get atom types from coordinate file
    # add atom types to sections
    for atom in get_atom_types(data["coord"]):
        if f"kind_{atom.lower()}" in sections["force_eval"]["subsys"]:
            sections["force_eval"]["subsys"][f"kind_{atom.lower()}"][
                "add"
            ] = True
        else:
            sys.exit(f"Atom type {atom} not supported by this script.")
    # if the dftu section is requested check if it is supported
    if data["dftu"] is not None:
        for atom in data["dftu"]:
            if atom not in get_atom_types(data["coord"]):
                sys.exit(
                    f"Atom type {atom} not present in the coordinate file."
                )
            else:
                sections["force_eval"]["subsys"][f"kind_{atom.lower()}"][
                    "dft_plus_u"
                ]["add"] = True

    # if xtb is used, add the xtb section and deactivate the dft section
    if data["func"] == "xtb":
        sections["force_eval"]["dft"]["qs"]["xtb"]["add"] = True
        sections["force_eval"]["dft"]["xc"]["add"] = False
    # else, add dft functional
    else:
        sections["force_eval"]["dft"]["xc"]["xc_functional"][data["func"]][
            "add"
        ] = True

    # check periodic efield
    if data["efield"] is not None:
        sections["force_eval"]["dft"]["periodic_efield"]["add"] = True

        # define efield dictionary
        efield_vectors = {
            "x": "1.0 0.0 0.0",
            "y": "0.0 1.0 0.0",
            "z": "0.0 0.0 1.0",
            "xy": "1.0 1.0 0.0",
            "xz": "1.0 0.0 1.0",
            "yz": "0.0 1.0 1.0",
            "xyz": "1.0 1.0 1.0",
        }

        if data["type"] == "bqb":
            # "n" means no electric field and is the case for ir, vcd and dipoles
            # "x", "y", "z" are the three components of the electric field needed for raman and roa
            fields = ["n", "x", "y", "z"]
    else:
        fields = [""]

    # add poisson section if system is not fully periodic
    if data["pbc"] == "none":
        sections["force_eval"]["dft"]["poisson"]["add"] = True

    # geometry optimization
    if data["joblist"][0]:

        # constraints for geometry optimization
        opt_constraints = {
            "loose": {
                "max_dr": 1.0e-2,
                "max_force": 3.0e-3,
                "rms_dr": 5.0e-3,
                "rms_force": 1.0e-3,
            },
            "normal": {
                "max_dr": 3.0e-3,
                "max_force": 4.5e-4,
                "rms_dr": 1.5e-3,
                "rms_force": 3.0e-4,
            },
            "tight": {
                "max_dr": 1.0e-3,
                "max_force": 1.5e-4,
                "rms_dr": 5.0e-4,
                "rms_force": 1.0e-4,
            },
        }

        # take a deep copy of the sections. Deep copy is necessary because of the nested structure of the dictionary.
        sections_geoopt = copy.deepcopy(sections)

        # motion
        # add geometry optimization and remove molecular dynamics, print
        sections_geoopt["motion"]["geo_opt"]["add"] = True
        sections_geoopt["motion"]["md"]["add"] = False
        sections_geoopt["motion"]["print"]["add"] = False

        lines = build_file([""], sections_geoopt)

        # replace keywords
        for i, line in enumerate(lines):
            if "${MAX_DR}" in line:
                lines[i] = line.replace(
                    "${MAX_DR}",
                    str(opt_constraints[data["opt_level"]]["max_dr"]),
                )
            if "${MAX_FORCE}" in line:
                lines[i] = line.replace(
                    "${MAX_FORCE}",
                    str(opt_constraints[data["opt_level"]]["max_force"]),
                )
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"] + "_opt"
                )
            if "${RMS_DR}" in line:
                lines[i] = line.replace(
                    "${RMS_DR}",
                    str(opt_constraints[data["opt_level"]]["rms_dr"]),
                )
            if "${RMS_FORCE}" in line:
                lines[i] = line.replace(
                    "${RMS_FORCE}",
                    str(opt_constraints[data["opt_level"]]["rms_force"]),
                )
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "GEO_OPT")

        # standard replacements
        lines = standard_replacements(lines, data)

        # write to file
        with open("geoopt.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # equilibration
    if data["joblist"][1]:
        # take a deep copy of the sections
        sections_eq = copy.deepcopy(sections)

        # ext_restart
        # read restart file if geoopt was done before
        sections_eq["ext_restart"]["add"] = data["joblist"][0]
        # add velocities if requested
        if data["velocity"] is not None:
            sections_eq["force_eval"]["subsys"]["velocity"]["add"] = True

        lines = build_file([""], sections_eq)

        # replace keywords
        for i, line in enumerate(lines):
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace("${ENSEMBLE}", "NVT")
            if "${FIELD_STRENGTH}" in line:
                lines[i] = line.replace(
                    "${FIELD_STRENGTH}", str(data["efield_strength"])
                )
            if "${FIELD_VECTOR}" in line:
                lines[i] = line.replace(
                    "${FIELD_VECTOR}", efield_vectors[data["efield"]]
                )
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_equi"]))
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"] + "_eq"
                )
            if "${REGION_THERMO}" in line:
                lines[i] = line.replace("${REGION_THERMO}", "MASSIVE")
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${TEMP}" in line:
                lines[i] = line.replace("${TEMP}", str(data["t_equi"]))
            if "${THERMO}" in line:
                lines[i] = line.replace("${THERMO}", data["thermo"])
            if "${TIMECON_THERMO}" in line:
                lines[i] = line.replace("${TIMECON_THERMO}", str(10))
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")
            if "&VELOCITY" in line and data["velocity"] is not None:
                with open(data["velocity"], encoding="utf-8") as v:
                    lines_to_add = v.read().splitlines()
                    for j in range(len(lines_to_add)):
                        lines.insert(
                            i + j + 1,
                            f"{'      '}{lines_to_add[j].split('#')[0].rstrip()}",
                        )

        # standard replacements
        lines = standard_replacements(lines, data)

        # write to file
        with open("eq.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # relaxation
    if data["joblist"][2]:
        # take a deep copy of the sections
        sections_relax = copy.deepcopy(sections)

        # ext_restart
        # if equilibration was executed before, read the restart file
        if data["joblist"][1]:
            sections_relax["ext_restart"]["add"] = True
            restart_ext = "_eq"

        lines = build_file([""], sections_relax)

        # replace keywords
        for i, line in enumerate(lines):
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace("${ENSEMBLE}", "NVT")
            if "${FIELD_STRENGTH}" in line:
                lines[i] = line.replace(
                    "${FIELD_STRENGTH}", str(data["efield_strength"])
                )
            if "${FIELD_VECTOR}" in line:
                lines[i] = line.replace(
                    "${FIELD_VECTOR}", efield_vectors[data["efield"]]
                )
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_relax"]))
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"] + "_relax"
                )
            if "${REGION_THERMO}" in line:
                lines[i] = line.replace("${REGION_THERMO}", "GLOBAL")
            if "${RESTART_NAME}" in line:
                lines[i] = line.replace(
                    "${RESTART_NAME}", data["project"] + restart_ext
                )
            if "${SCFGUESS}" in line:
                if sections_relax["ext_restart"]["add"]:
                    lines[i] = line.replace("${SCFGUESS}", "RESTART")
                else:
                    lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${TEMP}" in line:
                lines[i] = line.replace("${TEMP}", str(data["t_relax"]))
            if "${THERMO}" in line:
                lines[i] = line.replace("${THERMO}", data["thermo"])
            if "${TIMECON_THERMO}" in line:
                lines[i] = line.replace("${TIMECON_THERMO}", str(50))
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")

        # standard replacements
        lines = standard_replacements(lines, data)
        # write to file
        with open("relax.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # production
    if data["joblist"][3]:
        # take a deep copy of the sections
        sections_prod = copy.deepcopy(sections)

        # motion
        # if NVE ensemble is selected, remove thermostat
        if data["ensemble"] == "NVE":
            sections_prod["motion"]["thermostat"]["add"] = False
        # print forces and velocities
        sections_prod["motion"]["print"]["forces"]["add"] = True
        sections_prod["motion"]["print"]["velocities"]["add"] = True
        # remove restart in case of adaptive sampling
        if data["type"] == "adapt-sampl":
            sections_prod["motion"]["print"]["restart"]["add"] = False
            sections_prod["motion"]["print"]["restart_history"]["add"] = False
        # force evaluation
        # enable wannier centers if requested
        sections_prod["force_eval"]["dft"]["localize"]["add"] = data["wannier"]
        # electron density output
        if any([data["bqb"], data["cube"], data["voronoi"]]):
            sections_prod["force_eval"]["dft"]["print"]["add"] = True
            if data["bqb"]:
                sections_prod["force_eval"]["dft"]["print"]["e_density_bqb"][
                    "add"
                ] = True
            if data["cube"]:
                sections_prod["force_eval"]["dft"]["print"]["e_density_cube"][
                    "add"
                ] = True
            if data["voronoi"]:
                sections_prod["force_eval"]["dft"]["print"]["voronoi"][
                    "add"
                ] = True
        # ext_restart
        if data["joblist"][2]:
            sections_prod["ext_restart"]["add"] = True
            restart_ext = "_relax"
        elif data["joblist"][1]:
            sections_prod["ext_restart"]["add"] = True
            restart_ext = "_eq"
        # velocity
        if data["velocity"] is not None:
            sections_prod["force_eval"]["subsys"]["velocity"]["add"] = True

        lines = build_file([""], sections_prod)

        # replace keywords
        for i, line in enumerate(lines):
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace(
                    "${ENSEMBLE}", data["ensemble"].upper()
                )
            if "${FIELD_STRENGTH}" in line:
                lines[i] = line.replace(
                    "${FIELD_STRENGTH}", str(data["efield_strength"])
                )
            if "${FIELD_VECTOR}" in line:
                lines[i] = line.replace(
                    "${FIELD_VECTOR}", efield_vectors[data["efield"]]
                )
            if "${HISTORY_BQB}" in line:
                lines[i] = line.replace(
                    "${HISTORY_BQB}", str(data["bqb_history"])
                )
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_prod"]))
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"] + "_prod"
                )
            if "${REGION_THERMO}" in line:
                lines[i] = line.replace("${REGION_THERMO}", "GLOBAL")
            if "${RESTART_NAME}" in line:
                lines[i] = line.replace(
                    "${RESTART_NAME}", data["project"] + restart_ext
                )
            if "${SCFGUESS}" in line:
                if sections_prod["ext_restart"]["add"]:
                    lines[i] = line.replace("${SCFGUESS}", "RESTART")
                else:
                    lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${TEMP}" in line:
                lines[i] = line.replace("${TEMP}", str(data["t_prod"]))
            if "${THERMO}" in line:
                lines[i] = line.replace("${THERMO}", data["thermo"])
            if "${TIMECON_THERMO}" in line:
                lines[i] = line.replace("${TIMECON_THERMO}", str(100))
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")
            if "&VELOCITY" in line and data["velocity"] is not None:
                with open(data["velocity"], encoding="utf-8") as v:
                    lines_to_add = v.read().splitlines()
                    for j in range(len(lines_to_add)):
                        lines.insert(
                            i + j + 1,
                            f"{'      '}{lines_to_add[j].split('#')[0].rstrip()}",
                        )
            if "${PRINT_WANNIER_EVERY}" in line:
                lines[i] = line.replace(
                    "${PRINT_WANNIER_EVERY}", str(data["print_wannier_every"])
                )

        # standard replacements
        lines = standard_replacements(lines, data)
        # write to file
        with open("prod.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # bqb file calculation
    if data["joblist"][4]:
        # take a deep copy of the sections
        sections_bqb = copy.deepcopy(sections)

        # spectra settings
        if data["spectrum"] == "ir":
            stride = 8
            overlap = 0
        elif data["spectrum"] == "raman":
            stride = 8
            overlap = 0
        elif data["spectrum"] == "vcd":
            stride = 1
            overlap = 2
        elif data["spectrum"] == "roa":
            stride = 1
            overlap = 2
        elif data["spectrum"] == "dipoles":
            stride = 1
            overlap = 0

        # motion
        # change ensemble
        sections_bqb["motion"]["md"]["thermostat"]["add"] = False
        sections_bqb["motion"]["md"]["reftraj"]["add"] = True
        # adjust print section
        sections_bqb["motion"]["print"]["cell"]["add"] = False
        sections_bqb["motion"]["print"]["forces"]["add"] = False
        sections_bqb["motion"]["print"]["trajectory"]["add"] = False
        sections_bqb["motion"]["print"]["velocities"]["add"] = False
        # electron density
        # bqb file calculation
        sections_bqb["force_eval"]["dft"]["print"]["add"] = True
        sections_bqb["force_eval"]["dft"]["print"]["e_density_bqb"][
            "add"
        ] = True
        # switch to cube file if requested
        if data["cube"]:
            sections_bqb["force_eval"]["dft"]["print"]["e_density_cube"][
                "add"
            ] = True
            sections_bqb["force_eval"]["dft"]["print"]["e_density_bqb"][
                "add"
            ] = False

        for k, vec in enumerate(fields):

            if vec in ["", "n"]:
                # add efield if requested
                sections_bqb["force_eval"]["dft"]["periodic_efield"][
                    "add"
                ] = False
            else:
                sections_bqb["force_eval"]["dft"]["periodic_efield"][
                    "add"
                ] = True

            # build default input file
            lines = build_file([""], sections_bqb)

            # replace keywords
            for i, line in enumerate(lines):
                if "${ENSEMBLE}" in line:
                    lines[i] = line.replace("${ENSEMBLE}", "REFTRAJ")
                if "${FIELD_STRENGTH}" in line:
                    lines[i] = line.replace(
                        "${FIELD_STRENGTH}", str(data["efield_strength"])
                    )
                if "${FIELD_VECTOR}" in line:
                    lines[i] = line.replace(
                        "${FIELD_VECTOR}", efield_vectors[vec]
                    )
                if "${FIRST_SNAPSHOT}" in line:
                    lines[i] = line.replace(
                        "${FIRST_SNAPSHOT}",
                        str(
                            data["start_from"]
                            + bqb_count * data["steps_bqb"] * stride
                        ),
                    )
                if "${HISTORY_BQB}" in line:
                    lines[i] = line.replace(
                        "${HISTORY_BQB}", str(data["bqb_history"])
                    )
                if "${LAST_SNAPSHOT}" in line:
                    lines[i] = line.replace(
                        "${LAST_SNAPSHOT}",
                        str(
                            data["start_from"]
                            + (bqb_count + 1) * data["steps_bqb"] * stride
                            + overlap
                            - stride
                        ),
                    )
                if "${NSTEPS}" in line:
                    lines[i] = line.replace(
                        "${NSTEPS}", str(data["steps_bqb"] + overlap)
                    )
                if "${PROJECT_NAME}" in line:
                    if len(fields) > 1:
                        lines[i] = line.replace(
                            "${PROJECT_NAME}",
                            data["project"] + f"_{bqb_count+1:02d}_{vec}",
                        )
                    else:
                        lines[i] = line.replace(
                            "${PROJECT_NAME}",
                            data["project"] + f"_{bqb_count+1:02d}",
                        )
                if "${SCFGUESS}" in line:
                    lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
                if "${STRIDE}" in line:
                    lines[i] = line.replace("${STRIDE}", str(stride))
                if "${TRAJ_FILE_NAME}" in line:
                    lines[i] = line.replace(
                        "${TRAJ_FILE_NAME}",
                        data["reftraj"],
                    )
                if "${TYPE}" in line:
                    lines[i] = line.replace("${TYPE}", "MD")

            # standard replacements
            lines = standard_replacements(lines, data)

            # special treatment for multiple fields
            if len(fields) > 1:
                # create directory for each field
                Path.mkdir(Path(f"{vec}_field"))

                # write to file
                with open(f"{vec}_field/bqb.inp", "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

                # copy the other (identical) files like coordinates and trajectory
                shutil.copy2(data["coord"], f"{vec}_field/")
                shutil.copy2(data["reftraj"], f"{vec}_field/")
                shutil.copy2(data["runscript"], f"{vec}_field/")

                # adjust the runscript and copy it
                os.system(
                    f"sed -i 's@{data['project']}_{bqb_count+1:02d}@{data['project']}_{bqb_count+1:02d}_{vec}@g' ./{vec}_field/{data['runscript']}"
                )

                if k == 3:
                    # remove the files from the main directory if they exist there (and were not copied from somewhere else)
                    Path.unlink(Path(f"./{data['coord']}"), missing_ok=True)
                    Path.unlink(
                        Path(f"./{data['runscript']}"), missing_ok=True
                    )
                    Path.unlink(Path(f"./{data['reftraj']}"), missing_ok=True)
            else:
                with open("bqb.inp", "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))

    # single point energy calculation
    if data["joblist"][5]:
        # take a deep copy of the sections
        sections_energy = copy.deepcopy(sections)

        # no motion
        sections_energy["motion"]["add"] = False

        # electronic density
        if data["bqb"]:
            sections_energy["force_eval"]["dft"]["print"]["add"] = True
            sections_energy["force_eval"]["dft"]["print"]["e_density_bqb"][
                "add"
            ] = True
        if data["cube"]:
            sections_energy["force_eval"]["dft"]["print"]["add"] = True
            sections_energy["force_eval"]["dft"]["print"]["e_density_cube"][
                "add"
            ] = True

        lines = build_file([""], sections_energy)

        # replace keywords
        for i, line in enumerate(lines):
            if "${HISTORY_BQB}" in line:
                lines[i] = line.replace("${HISTORY_BQB}", str(1))
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"] + "_energy"
                )
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "ENERGY_FORCE")

        # standard replacements
        lines = standard_replacements(lines, data)
        # write to file
        with open("energy.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def standard_replacements(
    lines: list[str], data: dict[str, Any], bqb_count: int = 0
) -> list[str]:
    """Replace standard keywords in the input files, i.e., keywords that are present in all types of input files.

    Parameters
    ----------
    lines : list[str]
        List of strings containing the input file.
    data : dict[str, Any]
        Dictionary containing the input parameters specified by the user.
    bqb_count : int, optional
        Counter for the bqb files, by default 0. Used to name the bqb files.

    Returns
    -------
    list[str]
        List of strings containing the input file with the standard keywords replaced.
    """

    idx_to_remove = []
    for i, line in enumerate(lines):
        if "ANGVEL_TOL" in line:
            if data["pbc"] != "none":
                idx_to_remove.append(i)
        if "${BASIS}" in line:
            lines[i] = line.replace("${BASIS}", data["basis"])
        if "${BOX_LENGTH}" in line:
            lines[i] = line.replace(
                "${BOX_LENGTH}",
                str(data["boxsize"][0])
                + " "
                + str(data["boxsize"][1])
                + " "
                + str(data["boxsize"][2]),
            )
        if "CENTER_COORDINATES" in line:
            if data["pbc"] == "xyz":
                idx_to_remove.append(i)
        if "${CHRG}" in line:
            if data["charge"] == 0:  # remove if default
                idx_to_remove.append(i)
            else:
                lines[i] = line.replace("${CHRG}", str(data["charge"]))
        if "${GRID_CUTOFF}" in line:
            lines[i] = line.replace("${GRID_CUTOFF}", str(data["grid_cutoff"]))
        if "${GRID_N}" in line:
            lines[i] = line.replace("${GRID_N}", str(data["grid_n"]))
        if "${GRID_REL_CUTOFF}" in line:
            lines[i] = line.replace(
                "${GRID_REL_CUTOFF}", str(data["grid_rel_cutoff"])
            )
        if "${L_ANG_QUANT_NUM}" in line:
            atom_type = lines[i - 4].split()[1]
            lines[i] = line.replace(
                "${L_ANG_QUANT_NUM}", str(data["dftu"][atom_type][0])
            )
        if "${MULT}" in line:
            if data["mult"] == 1:  # remove if default
                idx_to_remove.append(i)
            else:
                lines[i] = line.replace("${MULT}", str(data["mult"]))
        if "${PBC}" in line:
            if data["pbc"] == "xyz":
                idx_to_remove.append(i)
            else:
                lines[i] = line.replace("${PBC}", data["pbc"].upper())
        if "${PLUS_U}" in line:
            if data["dftu"] is None:
                idx_to_remove.append(i)
            else:
                lines[i] = line.replace("${PLUS_U}", "MULLIKEN")
        if "${POISSON_SOLVER}" in line:
            lines[i] = line.replace(
                "${POISSON_SOLVER}", data["poisson_solver"]
            )
        if "${PP_FUNC}" in line:
            lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
        if "${PRINT_BQB_EVERY}" in line:
            lines[i] = line.replace(
                "${PRINT_BQB_EVERY}", str(data["print_bqb_every"])
            )
        if "${PRINT_CUBE_EVERY}" in line:
            lines[i] = line.replace(
                "${PRINT_CUBE_EVERY}", str(data["print_cube_every"])
            )
        if "${PRINT_VORONOI_EVERY}" in line:
            lines[i] = line.replace(
                "${PRINT_VORONOI_EVERY}", str(data["print_voronoi_every"])
            )
        if "${QS_METHOD}" in line:
            if data["qs_method"] == "GPW":
                idx_to_remove.append(i)  # remove if default
            else:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
        if "${SEED}" in line:
            if data["seed"] == 2000:
                idx_to_remove.append(i)  # remove if default
            else:
                lines[i] = line.replace("${SEED}", str(data["seed"]))
        if "${SIMBOX_XYZ}" in line:
            lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])
        if "${TIMESTEP}" in line:
            lines[i] = line.replace("${TIMESTEP}", str(data["timestep"]))
        if "${UKS}" in line:
            if not data["uks"]:
                idx_to_remove.append(i)  # remove if default
            else:
                lines[i] = line.replace("${UKS}", str(data["uks"]).upper())
        if "${U_MINUS_J}" in line:
            atom_type = lines[i - 5].split()[1]
            lines[i] = line.replace(
                "${U_MINUS_J}", str(data["dftu"][atom_type][1])
            )

    # remove unnecessary keywords
    for i in sorted(idx_to_remove, reverse=True):
        lines.pop(i)

    return lines
