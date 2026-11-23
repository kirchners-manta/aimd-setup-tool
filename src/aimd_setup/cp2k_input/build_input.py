"""
Build the CP2K input files for the AIMD setup tool.

Each input is assembled as a nested dictionary that mirrors the CP2K section tree and
is written with the serializer of pycp2k (``cp2k.input_to_string``). Its conventions:

- a dict is a section, a list of dicts repeats a section,
- the key ``"_"`` holds the section parameter (``{"_": "H"}`` gives ``&KIND H``),
- the key ``"_lines"`` holds raw lines (used for velocities),
- the value ``None`` gives a bare keyword, a list gives several values on one line.

The serializer does not validate the input; the tests check it against the CP2K schema.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from cp2k import input_to_string

Section = dict[str, Any]

# valence electrons of the GTH pseudopotentials (the "q" in GTH-<FUNC>-q<n>);
# the order of this dict sets the order of the KIND sections in the input
VALENCE_ELECTRONS = {
    "H": 1,
    "D": 1,
    "Li": 3,
    "B": 3,
    "C": 4,
    "N": 5,
    "O": 6,
    "F": 7,
    "Na": 9,
    "Mg": 10,
    "P": 5,
    "S": 6,
    "Cl": 7,
    "K": 9,
    "Ti": 12,
    "Fe": 16,
    "Co": 17,
    "Zn": 12,
    "Br": 7,
}

# content of the XC_FUNCTIONAL section per functional
XC_FUNCTIONALS: dict[str, Section] = {
    "blyp": {"GGA_X_B88": {}, "GGA_C_LYP": {}},
    "bp": {"_": "BP"},
    "pade": {"_": "PADE"},
    "pbe": {"PBE": {"PARAMETRIZATION": "ORIG"}},
    "pbe0": {"HYB_GGA_XC_PBEH": {}},
    "r2scan": {"MGGA_X_R2SCAN": {}, "MGGA_C_R2SCAN": {}},
    "revpbe": {"PBE": {"PARAMETRIZATION": "REVPBE"}},
    "scan": {"MGGA_C_SCAN": {}, "MGGA_X_SCAN": {}},
}

EFIELD_VECTORS = {
    "x": [1.0, 0.0, 0.0],
    "y": [0.0, 1.0, 0.0],
    "z": [0.0, 0.0, 1.0],
    "xy": [1.0, 1.0, 0.0],
    "xz": [1.0, 0.0, 1.0],
    "yz": [0.0, 1.0, 1.0],
    "xyz": [1.0, 1.0, 1.0],
}

# geometry optimization convergence criteria (bohr, hartree/bohr)
OPT_CRITERIA = {
    "loose": {
        "MAX_DR": 1.0e-2,
        "MAX_FORCE": 3.0e-3,
        "RMS_DR": 5.0e-3,
        "RMS_FORCE": 1.0e-3,
    },
    "normal": {
        "MAX_DR": 3.0e-3,
        "MAX_FORCE": 4.5e-4,
        "RMS_DR": 1.5e-3,
        "RMS_FORCE": 3.0e-4,
    },
    "tight": {
        "MAX_DR": 1.0e-3,
        "MAX_FORCE": 1.5e-4,
        "RMS_DR": 5.0e-4,
        "RMS_FORCE": 1.0e-4,
    },
}

# sampling of the reference trajectory per spectrum: stride between snapshots,
# overlap between consecutive chunks (in steps), and field directions
# ("" = no field, "n" = zero-field reference of a field series)
SPECTRUM_SETTINGS: dict[str, tuple[int, int, list[str]]] = {
    "ir": (8, 0, [""]),
    "raman": (8, 0, ["n", "x", "y", "z"]),
    "vcd": (1, 2, [""]),
    "roa": (1, 2, ["n", "x", "y", "z"]),
    "dipoles": (1, 0, [""]),
}

# CP2K's default seed; the SEED keyword is only written for other values
DEFAULT_SEED = 2000


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


def each_md(every: int) -> Section:
    """Print frequency subsection: print every ``every`` MD steps.

    Parameters
    ----------
    every : int
        Print interval in MD steps.

    Returns
    -------
    Section
        The ``EACH`` section.
    """
    return {"EACH": {"MD": every}}


def global_section(
    data: dict[str, Any], project: str, run_type: str
) -> Section:
    """Build the GLOBAL section.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    project : str
        CP2K project name, used as prefix of all output files.
    run_type : str
        CP2K run type, e.g. MD, GEO_OPT, ENERGY_FORCE.

    Returns
    -------
    Section
        The GLOBAL section.
    """
    section: Section = {
        "ALLTOALL_SGL": "YES",
        "FFTW_PLAN_TYPE": "PATIENT",
        "PREFERRED_FFT_LIBRARY": "FFTW",
        "PRINT_LEVEL": "LOW",
        "PROJECT": project,
        "RUN_TYPE": run_type,
    }
    if data["seed"] != DEFAULT_SEED:
        section["SEED"] = data["seed"]
    return section


def kind_sections(data: dict[str, Any]) -> list[Section]:
    """Build one KIND section per element in the coordinate file.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.

    Returns
    -------
    list[Section]
        KIND sections in the order of ``VALENCE_ELECTRONS``.

    Raises
    ------
    SystemExit
        If the coordinates contain an element without pseudopotential data, or if
        DFT+U is requested for an element that is not in the coordinates.
    """
    atom_types = get_atom_types(data["coord"])
    for atom in atom_types:
        if atom not in VALENCE_ELECTRONS:
            sys.exit(f"Atom type {atom} not supported by this script.")
    dftu = data["dftu"] or {}
    for atom in dftu:
        if atom not in atom_types:
            sys.exit(f"Atom type {atom} not present in the coordinate file.")

    kinds = []
    for element, valence in VALENCE_ELECTRONS.items():
        if element not in atom_types:
            continue
        kind: Section = {
            "_": element,
            "BASIS_SET": ["ORB", data["basis"]],
            "POTENTIAL": f"GTH-{data['pp_func']}-q{valence}",
        }
        if element == "D":
            # deuterium: hydrogen basis and pseudopotential with the deuteron mass
            kind |= {"ELEMENT": "H", "MASS": 2.0141}
        if element in dftu:
            l_quantum_number, u_minus_j = dftu[element]
            kind["DFT_PLUS_U"] = {
                "_": "ON",
                "L": l_quantum_number,
                "U_MINUS_J": u_minus_j,
            }
        kinds.append(kind)
    return kinds


def subsys_section(data: dict[str, Any]) -> Section:
    """Build the SUBSYS section: cell, kinds and coordinates.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.

    Returns
    -------
    Section
        The SUBSYS section.
    """
    cell: Section = {"ABC": data["boxsize"]}
    topology: Section = {
        "COORD_FILE_NAME": data["coord"],
        "COORD_FILE_FORMAT": "XYZ",
    }
    if data["pbc"] == "none":
        cell["PERIODIC"] = "NONE"
        # an isolated system is placed in the middle of the box
        topology["CENTER_COORDINATES"] = {}
    return {"CELL": cell, "KIND": kind_sections(data), "TOPOLOGY": topology}


def dft_section(
    data: dict[str, Any], scf_guess: str, efield: str | None
) -> Section:
    """Build the DFT section (or its xTB variant).

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    scf_guess : str
        Initial guess of the wave function, ATOMIC or RESTART.
    efield : str | None
        Direction of a periodic electric field (key of ``EFIELD_VECTORS``), or None
        for no field.

    Returns
    -------
    Section
        The DFT section.
    """
    dft: Section = {
        "BASIS_SET_FILE_NAME": "BASIS_MOLOPT",
        "POTENTIAL_FILE_NAME": "GTH_POTENTIALS",
    }
    if data["charge"] != 0:
        dft["CHARGE"] = data["charge"]
    if data["mult"] != 1:
        dft["MULTIPLICITY"] = data["mult"]
    if data["uks"]:
        dft["UKS"] = True
    if data["dftu"] is not None:
        dft["PLUS_U_METHOD"] = "MULLIKEN"

    dft["MGRID"] = {
        "CUTOFF": data["grid_cutoff"],
        "NGRIDS": data["grid_n"],
        "REL_CUTOFF": data["grid_rel_cutoff"],
    }
    if efield is not None:
        dft["PERIODIC_EFIELD"] = {
            "INTENSITY": data["efield_strength"],
            "POLARISATION": EFIELD_VECTORS[efield],
        }
    if data["pbc"] == "none":
        dft["POISSON"] = {
            "PERIODIC": "NONE",
            "POISSON_SOLVER": data["poisson_solver"],
        }

    dft["QS"] = {"EPS_DEFAULT": 1.0e-12, "EXTRAPOLATION_ORDER": 4}
    if data["func"] == "xtb":
        # settings from https://manual.cp2k.org/trunk/methods/semiempiricals/xtb.html
        dft["QS"] |= {
            "METHOD": "XTB",
            "XTB": {
                "CHECK_ATOMIC_CHARGES": False,
                "DO_EWALD": True,
                "USE_HALOGEN_CORRECTION": True,
            },
        }

    dft["SCF"] = {
        "EPS_SCF": 1.0e-6,
        "MAX_SCF": 20,
        "SCF_GUESS": scf_guess,
        "OT": {"MINIMIZER": "DIIS", "PRECONDITIONER": "FULL_SINGLE_INVERSE"},
        # the outer EPS_SCF must not be smaller than the inner one
        "OUTER_SCF": {"MAX_SCF": 20, "EPS_SCF": 1.0e-6},
    }

    if data["func"] != "xtb":
        dft["XC"] = {
            "VDW_POTENTIAL": {
                "POTENTIAL_TYPE": "PAIR_POTENTIAL",
                "PAIR_POTENTIAL": {
                    "PARAMETER_FILE_NAME": "dftd3.dat",
                    "REFERENCE_FUNCTIONAL": data["pp_func"],
                    "TYPE": "DFTD3(BJ)",
                },
            },
            "XC_FUNCTIONAL": XC_FUNCTIONALS[data["func"]],
            "XC_GRID": {"XC_DERIV": "NN10_SMOOTH", "XC_SMOOTH_RHO": "NN10"},
        }
    return dft


def force_eval_section(
    data: dict[str, Any], scf_guess: str, efield: str | None
) -> Section:
    """Build the FORCE_EVAL section.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    scf_guess : str
        Initial guess of the wave function, ATOMIC or RESTART.
    efield : str | None
        Direction of a periodic electric field, or None for no field.

    Returns
    -------
    Section
        The FORCE_EVAL section.
    """
    return {
        "METHOD": "QS",
        "DFT": dft_section(data, scf_guess, efield),
        "SUBSYS": subsys_section(data),
    }


def density_print_section(
    data: dict[str, Any],
    *,
    bqb: bool,
    cube: bool,
    voronoi: bool,
    bqb_history: int,
) -> Section:
    """Build the DFT/PRINT section for electron density output.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    bqb : bool
        Write the density in compressed BQB format.
    cube : bool
        Write the density as cube files.
    voronoi : bool
        Write Voronoi integration results.
    bqb_history : int
        Number of previous frames the BQB compression uses.

    Returns
    -------
    Section
        The PRINT section, empty if no output is requested.
    """
    section: Section = {}
    if bqb:
        section["E_DENSITY_BQB"] = {
            "FILENAME": "=edens.bqb",
            "HISTORY": bqb_history,
            **each_md(data["print_bqb_every"]),
        }
    if cube:
        section["E_DENSITY_CUBE"] = {
            "APPEND": None,
            "FILENAME": "=edens.cube",
            **each_md(data["print_cube_every"]),
        }
    if voronoi:
        section["VORONOI"] = {
            "APPEND": None,
            "FILENAME": "=traj.voronoi",
            "OUTPUT_EMP": None,
            **each_md(data["print_voronoi_every"]),
        }
    return section


def localize_section(data: dict[str, Any]) -> Section:
    """Build the LOCALIZE section for Wannier centers.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.

    Returns
    -------
    Section
        The LOCALIZE section.
    """
    return {
        "MAX_ITER": 2000,
        # CRAZY falls back to JACOBI if it fails
        "METHOD": "CRAZY",
        "USE_HISTORY": None,
        "PRINT": {
            "WANNIER_CENTERS": {
                "IONS+CENTERS": None,
                "FILENAME": "=wannier.xyz",
                **each_md(data["print_wannier_every"]),
            }
        },
    }


def velocity_section(velocity_file: str) -> Section:
    """Build the VELOCITY section from a file with one velocity per line.

    Parameters
    ----------
    velocity_file : str
        Path to the velocity file. Comments (``#``) and empty lines are skipped.

    Returns
    -------
    Section
        The VELOCITY section.
    """
    lines = Path(velocity_file).read_text(encoding="utf-8").splitlines()
    stripped = (line.split("#")[0].strip() for line in lines)
    return {"_lines": [line for line in stripped if line]}


def md_section(data: dict[str, Any], ensemble: str, steps: int) -> Section:
    """Build the MD section without thermostat.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    ensemble : str
        CP2K ensemble, e.g. NVT, NVE, REFTRAJ.
    steps : int
        Number of MD steps.

    Returns
    -------
    Section
        The MD section.
    """
    md: Section = {}
    if data["pbc"] == "none":
        # overall rotation is only a conserved quantity without periodic images
        md["ANGVEL_TOL"] = 1.0e-12
    md |= {
        "COMVEL_TOL": 1.0e-12,
        "ENSEMBLE": ensemble,
        "STEPS": steps,
        "TIMESTEP": data["timestep"],
    }
    return md


def thermostat_keywords(
    data: dict[str, Any], temperature: float, region: str, timecon: int
) -> Section:
    """Build the temperature keyword and THERMOSTAT section of the MD section.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    temperature : float
        Target temperature in K.
    region : str
        Thermostat region: MASSIVE (one per degree of freedom, fast equilibration)
        or GLOBAL.
    timecon : int
        Time constant of the thermostat in fs.

    Returns
    -------
    Section
        Entries to merge into the MD section.
    """
    return {
        "TEMPERATURE": temperature,
        "THERMOSTAT": {
            "REGION": region,
            "TYPE": data["thermo"],
            # written for every thermostat type, as in earlier versions of this tool
            "NOSE": {"TIMECON": timecon},
        },
    }


def motion_print_section(
    *,
    trajectory: bool = True,
    forces_velocities: bool = False,
    restart: bool = True,
) -> Section:
    """Build the MOTION/PRINT section.

    Parameters
    ----------
    trajectory : bool, optional
        Write positions every step, by default True.
    forces_velocities : bool, optional
        Write forces and velocities every step, by default False.
    restart : bool, optional
        Write restart files (every step, and a history every 500 steps), by
        default True.

    Returns
    -------
    Section
        The PRINT section.
    """
    section: Section = {}
    if forces_velocities:
        section["FORCES"] = each_md(1)
    if restart:
        section["RESTART"] = each_md(1)
        section["RESTART_HISTORY"] = each_md(500)
    if trajectory:
        section["TRAJECTORY"] = each_md(1)
    if forces_velocities:
        section["VELOCITIES"] = each_md(1)
    return section


def ext_restart_section(project: str) -> Section:
    """Build the EXT_RESTART section that continues from a previous run.

    Parameters
    ----------
    project : str
        Project name of the previous run.

    Returns
    -------
    Section
        The EXT_RESTART section.
    """
    return {"RESTART_FILE_NAME": f"{project}-1.restart"}


def geoopt_input(data: dict[str, Any]) -> Section:
    """Build the input of a geometry optimization.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.

    Returns
    -------
    Section
        The complete input tree.
    """
    criteria = OPT_CRITERIA[data["opt_level"]]
    return {
        "GLOBAL": global_section(data, f"{data['project']}_opt", "GEO_OPT"),
        "MOTION": {
            "GEO_OPT": {
                "MAX_DR": criteria["MAX_DR"],
                "MAX_FORCE": criteria["MAX_FORCE"],
                "MAX_ITER": 200,
                "OPTIMIZER": "CG",
                "RMS_DR": criteria["RMS_DR"],
                "RMS_FORCE": criteria["RMS_FORCE"],
                "TYPE": "MINIMIZATION",
            }
        },
        "FORCE_EVAL": force_eval_section(data, "ATOMIC", data["efield"]),
    }


def equilibration_input(data: dict[str, Any]) -> Section:
    """Build the input of the equilibration run (NVT, massive thermostat).

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.

    Returns
    -------
    Section
        The complete input tree.
    """
    md = md_section(data, "NVT", data["steps_equi"])
    md |= thermostat_keywords(data, data["t_equi"], "MASSIVE", 10)
    force_eval = force_eval_section(data, "ATOMIC", data["efield"])
    if data["velocity"] is not None:
        force_eval["SUBSYS"]["VELOCITY"] = velocity_section(data["velocity"])
    return {
        "GLOBAL": global_section(data, f"{data['project']}_eq", "MD"),
        "MOTION": {"MD": md, "PRINT": motion_print_section()},
        "FORCE_EVAL": force_eval,
    }


def relaxation_input(data: dict[str, Any], restart: str | None) -> Section:
    """Build the input of the relaxation run (NVT at the target temperature).

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    restart : str | None
        Project name of the run to continue from, or None to start fresh.

    Returns
    -------
    Section
        The complete input tree.
    """
    md = md_section(data, "NVT", data["steps_relax"])
    md |= thermostat_keywords(data, data["t_relax"], "GLOBAL", 50)
    scf_guess = "ATOMIC" if restart is None else "RESTART"
    tree: Section = {
        "GLOBAL": global_section(data, f"{data['project']}_relax", "MD"),
        "MOTION": {"MD": md, "PRINT": motion_print_section()},
        "FORCE_EVAL": force_eval_section(data, scf_guess, data["efield"]),
    }
    if restart is not None:
        tree["EXT_RESTART"] = ext_restart_section(restart)
    return tree


def production_input(data: dict[str, Any], restart: str | None) -> Section:
    """Build the input of the production run (also used for adaptive sampling).

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    restart : str | None
        Project name of the run to continue from, or None to start fresh.

    Returns
    -------
    Section
        The complete input tree.
    """
    md = md_section(data, data["ensemble"], data["steps_prod"])
    if data["ensemble"] != "NVE":
        md |= thermostat_keywords(data, data["t_prod"], "GLOBAL", 100)
    # adaptive sampling runs are too short to need restart files
    motion_print = motion_print_section(
        forces_velocities=True, restart=data["type"] != "adapt-sampl"
    )

    scf_guess = "ATOMIC" if restart is None else "RESTART"
    force_eval = force_eval_section(data, scf_guess, data["efield"])
    if data["wannier"]:
        force_eval["DFT"]["LOCALIZE"] = localize_section(data)
    density_print = density_print_section(
        data,
        bqb=data["bqb"],
        cube=data["cube"],
        voronoi=data["voronoi"],
        bqb_history=data["bqb_history"],
    )
    if density_print:
        force_eval["DFT"]["PRINT"] = density_print
    if data["velocity"] is not None:
        force_eval["SUBSYS"]["VELOCITY"] = velocity_section(data["velocity"])

    tree: Section = {
        "GLOBAL": global_section(data, f"{data['project']}_prod", "MD"),
        "MOTION": {"MD": md, "PRINT": motion_print},
        "FORCE_EVAL": force_eval,
    }
    if restart is not None:
        tree["EXT_RESTART"] = ext_restart_section(restart)
    return tree


def bqb_input(
    data: dict[str, Any], bqb_count: int, field: str, project: str
) -> Section:
    """Build the input that recomputes densities along a reference trajectory.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    bqb_count : int
        Index of the trajectory chunk handled by this input.
    field : str
        Field direction: "" (no field), "n" (zero-field reference) or a key of
        ``EFIELD_VECTORS``.
    project : str
        CP2K project name.

    Returns
    -------
    Section
        The complete input tree.
    """
    stride, overlap, _ = SPECTRUM_SETTINGS[data["spectrum"]]
    chunk_start = data["start_from"] + bqb_count * data["steps_bqb"] * stride
    md = md_section(data, "REFTRAJ", data["steps_bqb"] + overlap)
    md["REFTRAJ"] = {
        "EVAL_ENERGY_FORCES": None,
        "FIRST_SNAPSHOT": chunk_start,
        "LAST_SNAPSHOT": chunk_start
        + data["steps_bqb"] * stride
        + overlap
        - stride,
        "STRIDE": stride,
        "TRAJ_FILE_NAME": data["reftraj"],
    }

    efield = None if field in ("", "n") else field
    force_eval = force_eval_section(data, "ATOMIC", efield)
    # the PRINT section is written even if empty, as in earlier versions
    force_eval["DFT"]["PRINT"] = density_print_section(
        data,
        # cube files replace the BQB output
        bqb=data["bqb"] and not data["cube"],
        cube=data["cube"],
        voronoi=data["voronoi"],
        bqb_history=data["bqb_history"],
    )
    return {
        "GLOBAL": global_section(data, project, "MD"),
        "MOTION": {"MD": md, "PRINT": motion_print_section(trajectory=False)},
        "FORCE_EVAL": force_eval,
    }


def energy_input(data: dict[str, Any]) -> Section:
    """Build the input of a single point energy and force calculation.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.

    Returns
    -------
    Section
        The complete input tree.
    """
    force_eval = force_eval_section(data, "ATOMIC", data["efield"])
    density_print = density_print_section(
        data, bqb=data["bqb"], cube=data["cube"], voronoi=False, bqb_history=1
    )
    if density_print:
        force_eval["DFT"]["PRINT"] = density_print
    return {
        "GLOBAL": global_section(
            data, f"{data['project']}_energy", "ENERGY_FORCE"
        ),
        "FORCE_EVAL": force_eval,
    }


def write_input(path: str | Path, tree: Section) -> None:
    """Serialize an input tree and write it to a file.

    Parameters
    ----------
    path : str | Path
        Output file.
    tree : Section
        The complete input tree.
    """
    Path(path).write_text(input_to_string(tree), encoding="utf-8")


def write_bqb_inputs(data: dict[str, Any], bqb_count: int) -> None:
    """Write the input(s) for one trajectory chunk of a BQB calculation.

    Spectra that need several field directions (Raman, ROA) get one subdirectory per
    direction, each with its own copy of coordinates, trajectory and runscript.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options.
    bqb_count : int
        Index of the trajectory chunk.
    """
    _, _, fields = SPECTRUM_SETTINGS[data["spectrum"]]
    job_name = f"{data['project']}_{bqb_count+1:02d}"

    if len(fields) == 1:
        write_input("bqb.inp", bqb_input(data, bqb_count, fields[0], job_name))
        return

    for field in fields:
        field_dir = Path(f"{field}_field")
        field_dir.mkdir()
        write_input(
            field_dir / "bqb.inp",
            bqb_input(data, bqb_count, field, f"{job_name}_{field}"),
        )
        for file in (data["coord"], data["reftraj"], data["runscript"]):
            shutil.copy2(file, field_dir)
        # give each field its own job name in the runscript
        runscript = field_dir / data["runscript"]
        runscript.write_text(
            runscript.read_text(encoding="utf-8").replace(
                job_name, f"{job_name}_{field}"
            ),
            encoding="utf-8",
        )
    # the shared copies are no longer needed in the chunk directory
    for file in (data["coord"], data["runscript"], data["reftraj"]):
        Path(file).unlink(missing_ok=True)


def generate_input_files(data: dict[str, Any], bqb_count: int = 0) -> None:
    """Generate the CP2K input files in the current directory.

    Parameters
    ----------
    data : dict[str, Any]
        Setup options. ``data["joblist"]`` holds one bool per job, in this order:
        geometry optimization, equilibration, relaxation, production, BQB
        calculation, single point energy.
    bqb_count : int, optional
        Index of the trajectory chunk for BQB calculations, by default 0.
    """
    run_geoopt, run_eq, run_relax, run_prod, run_bqb, run_energy = data[
        "joblist"
    ]
    project = data["project"]

    if run_geoopt:
        write_input("geoopt.inp", geoopt_input(data))
    if run_eq:
        write_input("eq.inp", equilibration_input(data))
    if run_relax:
        restart = f"{project}_eq" if run_eq else None
        write_input("relax.inp", relaxation_input(data, restart))
    if run_prod:
        if run_relax:
            restart = f"{project}_relax"
        elif run_eq:
            restart = f"{project}_eq"
        else:
            restart = None
        write_input("prod.inp", production_input(data, restart))
    if run_bqb:
        write_bqb_inputs(data, bqb_count)
    if run_energy:
        write_input("energy.inp", energy_input(data))
