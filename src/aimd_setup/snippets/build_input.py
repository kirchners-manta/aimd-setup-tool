"""
Script to build input files for CP2K simulations, based on pre-defined input snippets.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, List


def get_default_sections() -> dict[str, Any]:
    """Get the default sections for the CP2K input file.

    Returns
    -------
    dict[str, Any]
        Dictionary containing all implemented sections for the CP2K input files.
        By default, some sections are disabled.
    """

    sections = {
        "global": {"add": True, "header": "header.inp", "keywords": "keywords.inp"},
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
                "print": {
                    "add": False,
                    "header": "header.inp",
                    "keywords": "keywords.inp",
                    "e_density_bqb": {
                        "add": False,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                    "e_density_cube": {
                        "add": False,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
                    },
                    "voronoi": {
                        "add": True,
                        "header": "header.inp",
                        "keywords": "keywords.inp",
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
    lines: List[str],
    sections: dict[str, Any],
    prefix: str = "",
) -> List[str]:
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
                    "r",
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
                    "r",
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

    with open(coord_file, "r", encoding="utf-8") as f:
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
            sections["force_eval"]["subsys"][f"kind_{atom.lower()}"]["add"] = True
        else:
            sys.exit(f"Atom type {atom} not supported.")

    # if xtb is used, add the xtb section and deactivate the dft section
    if data["func"] == "xtb":
        sections["force_eval"]["dft"]["qs"]["xtb"]["add"] = True
        sections["force_eval"]["dft"]["xc"]["add"] = False
    # else, add dft functional
    else:
        sections["force_eval"]["dft"]["xc"]["xc_functional"][data["func"]]["add"] = True

    # geometry optimization
    if data["joblist"][0]:
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
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"]
                )  # only one replacement necessary
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "GEOOPT")
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${PP_FUNC}" in line:
                lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
            if "${BASIS}" in line:
                lines[i] = line.replace("${BASIS}", data["basis"])
            if "${BOX_LENGTH}" in line:
                lines[i] = line.replace("${BOX_LENGTH}", data["boxsize"])
            if "${SIMBOX_XYZ}" in line:
                lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])

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
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace(
                    "${PROJECT_NAME}", data["project"]
                )  # only one replacement necessary
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace("${ENSEMBLE}", "NVT")
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_equi"]))
            if "${TEMP}" in line:
                lines[i] = line.replace("${TEMP}", str(data["t_equi"]))
            if "${REGION_THERMO}" in line:
                lines[i] = line.replace("${REGION_THERMO}", "MASSIVE")
            if "${THERMO}" in line:
                lines[i] = line.replace("${THERMO}", data["thermo"])
            if "${TIMECON_THERMO}" in line:
                lines[i] = line.replace("${TIMECON_THERMO}", str(10))
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
            if "${SCFGUESS}" in line:
                if data["joblist"][0]:
                    lines[i] = line.replace("${SCFGUESS}", "RESTART")
                else:
                    lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${PP_FUNC}" in line:
                lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
            if "${BASIS}" in line:
                lines[i] = line.replace("${BASIS}", data["basis"])
            if "${BOX_LENGTH}" in line:
                lines[i] = line.replace("${BOX_LENGTH}", data["boxsize"])
            if "${SIMBOX_XYZ}" in line:
                lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])
            if "&VELOCITY" in line and data["velocity"] is not None:
                with open(data["velocity"], "r", encoding="utf-8") as v:
                    lines_to_add = v.read().splitlines()
                    print(i)
                    for j in range(len(lines_to_add)):
                        lines.insert(
                            i + j + 1,
                            f"{'      '}{lines_to_add[j].split('#')[0].rstrip()}",
                        )
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])

        # write to file
        with open("eq.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # relaxation
    if data["joblist"][2]:
        # take a deep copy of the sections
        sections_relax = copy.deepcopy(sections)

        # ext_restart
        sections_relax["ext_restart"]["add"] = True

        lines = build_file([""], sections_relax)

        # replace keywords
        for i, line in enumerate(lines):
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace("${PROJECT_NAME}", data["project"])
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace("${ENSEMBLE}", "NVT")
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_relax"]))
            if "${TEMP}" in line:
                lines[i] = line.replace("${TEMP}", str(data["t_relax"]))
            if "${REGION_THERMO}" in line:
                lines[i] = line.replace("${REGION_THERMO}", "GLOBAL")
            if "${THERMO}" in line:
                lines[i] = line.replace("${THERMO}", data["thermo"])
            if "${TIMECON_THERMO}" in line:
                lines[i] = line.replace("${TIMECON_THERMO}", str(50))
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "RESTART")
            if "${PP_FUNC}" in line:
                lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
            if "${BASIS}" in line:
                lines[i] = line.replace("${BASIS}", data["basis"])
            if "${BOX_LENGTH}" in line:
                lines[i] = line.replace("${BOX_LENGTH}", data["boxsize"])
            if "${SIMBOX_XYZ}" in line:
                lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])

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
        # enable wannier centers if requested
        sections_prod["force_eval"]["dft"]["localize"]["add"] = data["wannier"]
        # electronic density
        if data["bqb"]:
            sections_prod["force_eval"]["dft"]["print"]["add"] = True
            sections_prod["force_eval"]["dft"]["print"]["e_density_bqb"]["add"] = True
        if data["cube"]:
            sections_prod["force_eval"]["dft"]["print"]["add"] = True
            sections_prod["force_eval"]["dft"]["print"]["e_density_cube"]["add"] = True

        # ext_restart
        sections_prod["ext_restart"]["add"] = True

        lines = build_file([""], sections_prod)

        # replace keywords
        for i, line in enumerate(lines):
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace("${PROJECT_NAME}", data["project"])
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace("${ENSEMBLE}", "NVT")
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_prod"]))
            if "${TEMP}" in line:
                lines[i] = line.replace("${TEMP}", str(data["t_prod"]))
            if "${REGION_THERMO}" in line:
                lines[i] = line.replace("${REGION_THERMO}", "GLOBAL")
            if "${THERMO}" in line:
                lines[i] = line.replace("${THERMO}", data["thermo"])
            if "${TIMECON_THERMO}" in line:
                lines[i] = line.replace("${TIMECON_THERMO}", str(100))
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "RESTART")
            if "${HISTORY_BQB}" in line:
                lines[i] = line.replace("${HISTORY_BQB}", str(10))
            if "${PP_FUNC}" in line:
                lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
            if "${BASIS}" in line:
                lines[i] = line.replace("${BASIS}", data["basis"])
            if "${BOX_LENGTH}" in line:
                lines[i] = line.replace("${BOX_LENGTH}", data["boxsize"])
            if "${SIMBOX_XYZ}" in line:
                lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])

        # write to file
        with open("prod.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # bqb file calculation
    if data["joblist"][4]:
        # take a deep copy of the sections
        sections_bqb = copy.deepcopy(sections)

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
        sections_bqb["force_eval"]["dft"]["print"]["e_density_bqb"]["add"] = True
        # switch to cube file if requested
        if data["cube"]:
            sections_bqb["force_eval"]["dft"]["print"]["e_density_cube"]["add"] = True
            sections_bqb["force_eval"]["dft"]["print"]["e_density_bqb"]["add"] = False

        # spectra settings
        if data["spectrum"] == "ir":
            calc_efield = False
            stride = 8
            overlap = 0
        elif data["spectrum"] == "raman":
            calc_efield = True
            stride = 8
            overlap = 0
            sys.exit("Raman spectrum not implemented yet.")
        elif data["spectrum"] == "vcd":
            calc_efield = False
            stride = 1
            overlap = 2
        elif data["spectrum"] == "roa":
            calc_efield = True
            stride = 1
            overlap = 2
            sys.exit("ROA spectrum not implemented yet.")
        elif data["spectrum"] == "dipoles":
            calc_efield = False
            stride = 1
            overlap = 0

        lines = build_file([""], sections_bqb)

        # replace keywords
        for i, line in enumerate(lines):
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace("${PROJECT_NAME}", data["project"])
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "MD")
            if "${ENSEMBLE}" in line:
                lines[i] = line.replace("${ENSEMBLE}", "REFTRAJ")
            if "${NSTEPS}" in line:
                lines[i] = line.replace("${NSTEPS}", str(data["steps_bqb"] + overlap))
            if "${FIRST_SNAPSHOT}" in line:
                lines[i] = line.replace(
                    "${FIRST_SNAPSHOT}",
                    str(data["start_from"] + bqb_count * data["steps_bqb"] * stride),
                )
            if "${STRIDE}" in line:
                lines[i] = line.replace("${STRIDE}", str(stride))
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
            if "${TRAJ_FILE_NAME}" in line:
                lines[i] = line.replace(
                    "${TRAJ_FILE_NAME}",
                    data["reftraj"],
                )
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${HISTORY_BQB}" in line:
                lines[i] = line.replace("${HISTORY_BQB}", str(10))
            if "${PP_FUNC}" in line:
                lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
            if "${BASIS}" in line:
                lines[i] = line.replace("${BASIS}", data["basis"])
            if "${BOX_LENGTH}" in line:
                lines[i] = line.replace("${BOX_LENGTH}", data["boxsize"])
            if "${SIMBOX_XYZ}" in line:
                lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])

        # write to file
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
            sections_energy["force_eval"]["dft"]["print"]["e_density_bqb"]["add"] = True
        if data["cube"]:
            sections_energy["force_eval"]["dft"]["print"]["add"] = True
            sections_energy["force_eval"]["dft"]["print"]["e_density_cube"][
                "add"
            ] = True

        lines = build_file([""], sections_energy)

        # replace keywords
        for i, line in enumerate(lines):
            if "${PROJECT_NAME}" in line:
                lines[i] = line.replace("${PROJECT_NAME}", data["project"])
            if "${TYPE}" in line:
                lines[i] = line.replace("${TYPE}", "ENERGY_FORCE")
            if "${QS_METHOD}" in line:
                lines[i] = line.replace("${QS_METHOD}", data["qs_method"])
            if "${SCFGUESS}" in line:
                lines[i] = line.replace("${SCFGUESS}", "ATOMIC")
            if "${HISTORY_BQB}" in line:
                lines[i] = line.replace("${HISTORY_BQB}", str(1))
            if "${PP_FUNC}" in line:
                lines[i] = line.replace("${PP_FUNC}", data["pp_func"])
            if "${BASIS}" in line:
                lines[i] = line.replace("${BASIS}", data["basis"])
            if "${BOX_LENGTH}" in line:
                lines[i] = line.replace("${BOX_LENGTH}", data["boxsize"])
            if "${SIMBOX_XYZ}" in line:
                lines[i] = line.replace("${SIMBOX_XYZ}", data["coord"])

        # write to file
        with open("energy.inp", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
