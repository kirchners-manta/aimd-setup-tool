"""
Main setup script for AIMD setup package.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any

from ..adjust_input import cp_runscript
from ..functions import make_project_dir
from ..snippets import generate_input_files


def setup_job(args: dict[str, Any]) -> int:
    """Main setup function for AIMD setup package.
    Checks and modifies arguments, prints them, and calls the necessary functions to build the input files.

    Parameters
    ----------
    args : dict[str, Any]
        Dictionary with the arguments from the command line, merged with the toml options.

    Returns
    -------
    int
        Exit code.
    """

    # project, coord file and box size are required, either from command line or toml file
    # box size can also be found in the coordinate file
    if args["project"] is None:
        sys.exit(
            " *** Project name is required through command line or toml file. Exiting."
        )
    if args["coord"] is None:
        sys.exit(
            " *** Coordinate file is required through command line or toml file. Exiting."
        )
    if args["boxsize"] is None:
        with open(args["coord"], encoding="utf-8") as f:
            # read the second line of the coordinate file
            line = f.readlines()[1].split()
            # convert the list of strings to a list of floats if it is not empty
            if len(line) > 0:
                args["boxsize"] = [float(i) for i in line]
            else:
                sys.exit(
                    " *** Box size is required through command line or toml file or in the second line of the coordinate file. Exiting."
                )
    else:
        # check given box dimensions
        # if only one is given -> cubic box, set all box dimensions to the same value
        if type(args["boxsize"]) == float or type(args["boxsize"]) == int:
            args["boxsize"] = [args["boxsize"]] * 3
        # if three are given -> orthorhombic boxsize
        elif len(args["boxsize"]) == 3:
            pass
        else:
            sys.exit(
                "Invalid box dimensions. Provide either one (cubic) or three (orthorhombic) box lengths."
            )

    # if REVPBE, use PBE for the pseudopotential, because CP2K does not have a REVPBE pseudopotential
    if args["func"] == "revpbe":
        pp_func = "PBE"
    # if R2SCAN, use SCAN for the pseudopotential, because CP2K does not have a R2SCAN pseudopotential
    elif args["func"] == "r2scan":
        pp_func = "SCAN"
    # otherwise, use the functional for the pseudopotential
    else:
        pp_func = args["func"].upper()
    args["pp_func"] = pp_func

    # if xTB is chosen, the QS method is xTB, else GPW
    if args["func"] == "xtb":
        qs_method = "XTB"
    else:
        qs_method = "GPW"

    # capitalize variables
    args["thermo"] = args["thermo"].upper()
    args["ensemble"] = args["ensemble"].upper()

    # basis set: if a cardinal number < 2, use SR-GTH
    if args["basis"] in ["tzvp", "tzv2p", "tzv2px"]:
        args["basis"] = args["basis"].upper() + "-MOLOPT-GTH"
    else:
        args["basis"] = args["basis"].upper() + "-MOLOPT-SR-GTH"

    # runscript name
    runscript_name = "run-cp2k-" + args["queue"] + ".sh"

    # project path
    project_dir = Path(args["project"]).resolve()
    args["project"] = project_dir.name

    # get absolute path of the coordinate file
    abs_coord = Path(args["coord"]).resolve()

    # get basename of the coordinate file
    args["coord"] = abs_coord.name

    # if bqb calculation, get absolute path of the reference trajectory file
    if args["type"] == "bqb":
        # get absolute path of the reference trajectory file
        abs_reftraj = Path(args["reftraj"]).resolve()

        # get basename of the reference trajectory file
        args["reftraj"] = abs_reftraj.name

        # if raman or roa spectrum is requested, set periodic efield to xyz
        if args["spectrum"] in ["raman", "roa"]:
            args["efield"] = "xyz"

    # if velocity is given, get the absolute path of the velocity file
    if args["velocity"] is not None:
        abs_velocity = Path(args["velocity"]).resolve()
        args["velocity"] = abs_velocity.name

    # check open shell calculation
    if args["mult"] > 1:
        args["uks"] = True

    # format dftu input
    if args["dftu"] is not None:
        dftu_dict = {}
        for i in range(0, len(args["dftu"]), 3):
            dftu_dict[args["dftu"][i]] = [
                int(args["dftu"][i + 1]),
                float(args["dftu"][i + 2]),
            ]
        args["dftu"] = dftu_dict

    # add additional arguments to the dictionary
    args["runscript"] = runscript_name
    args["qs_method"] = qs_method

    # adjust bqb history parameter if necessary
    if (
        (args["type"] == "bqb" and args["steps_bqb"] < 10)
        or args["type"] == "adapt-sampl"
        or (args["type"] == "aimd" and args["bqb"] and args["steps_prod"] < 10)
    ):
        args["bqb_history"] = 1
    else:
        args["bqb_history"] = 10

    # poisson solver
    if args["pbc"] == "xyz":
        args["poisson_solver"] = "PERIODIC"
    elif args["pbc"] == "none":
        args["poisson_solver"] = "WAVELET"

    #############################################

    # print the arguments relevant for the type of calculation
    # general arguments are printed first
    print("The following arguments were given (including defaults):")
    print("Project name:", args["project"])
    print("Box size [Angstrom]:", args["boxsize"])
    print("Periodic boundary conditions:", args["pbc"].upper())
    print("Coordinate file:", args["coord"])
    print("Charge:", args["charge"])
    if args["uks"]:
        print("Multiplicity:", args["mult"], "(open shell calculation)")
    else:
        print("Multiplicity:", args["mult"])
    print("QS method:", qs_method)
    if qs_method == "GPW":
        print("Density functional:", args["func"].upper())
        print("Pseudopotential:", pp_func)
        print("Basis set:", args["basis"])
        if args["dftu"] is not None:
            print(
                "DFT+U:",
                [f"{k}: L={v[0]}, U-J={v[1]} eV" for k, v in args["dftu"].items()],
            )

    # arguments that are only needed for a certain type of calculation are printed last
    if args["type"] == "aimd":
        # define which jobs are to be executed
        exec_geoopt = False
        exec_eq = not args["no_equi"]
        exec_relax = not args["no_relax"]
        exec_prod = not args["no_prod"]
        exec_bqb = False
        exec_energy = False

        print("Type of calculation: AIMD simulation")
        if not args["no_equi"]:
            print("Equilibration steps:", args["steps_equi"])
            print("Equilibration temperature [K]:", args["t_equi"])
        if not args["no_relax"]:
            print("Relaxation steps:", args["steps_relax"])
            print("Relaxation temperature [K]:", args["t_relax"])
        if not args["no_prod"]:
            print("Production steps:", args["steps_prod"])
            print("Production temperature [K]:", args["t_prod"])
        if not args["no_equi"]:
            print("Thermodynamic ensemble in equilibration:", "NVT")
            print("Thermostat:", args["thermo"])
        if not args["no_prod"]:
            print("Thermodynamic ensemble in production:", args["ensemble"])
            print("Thermostat:", args["thermo"])
        if args["velocity"] is not None:
            print("Initial velocities:", args["velocity"])
        print("Print BQB file:", args["bqb"])
        print("Calculate Wannier functions:", args["wannier"])

    elif args["type"] == "bqb":
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = True
        exec_energy = False

        print("Type of calculation: BQB file production")
        print("Reference trajectory:", args["reftraj"])
        print("Process Trajectory from step:", args["start_from"])
        print("Bqb files:", args["n_bqb"])
        print("Steps per bqb file:", args["steps_bqb"])
        print("Spectrum:", args["spectrum"])

    elif args["type"] == "energy":
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = False
        exec_energy = True

        print("Type of calculation: Single point energy calculation")
        print("Energy convergence criterion [Hartree]:", args["e_conv"])

    elif args["type"] == "adapt-sampl":
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = True
        exec_bqb = False
        exec_energy = False

        # set extra arguments specific to this type of calculation
        args["steps_prod"] = 2
        args["bqb"] = True
        # velocity is required
        if args["velocity"] is None:
            sys.exit(
                " *** Velocity file is required for adaptive sampling. Watch the velocity format. Exiting."
            )

        print("Type of calculation: Adaptive sampling (with Leipzig people)")
        print("Production steps:", args["steps_prod"])
        print("Production temperature [K]:", args["t_prod"])
        print("Print BQB file:", args["bqb"])

    elif args["type"] == "geoopt":
        exec_geoopt = True
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = False
        exec_energy = False

        print("Type of calculation: Geometry optimization")
        print("Convergence criteria:", args["opt_level"])

    # electric field settings
    if args["efield"] is not None:
        print("Periodic E-field:", args["efield"])
        print("E-field strength [a.u.]:", args["efield_strength"])

    # HPC information
    print("Queue:", args["queue"])
    print("Runscript:", runscript_name)
    print("CPU cores:", args["cpu"])
    print("")

    # add joblist
    args["joblist"] = [
        exec_geoopt,
        exec_eq,
        exec_relax,
        exec_prod,
        exec_bqb,
        exec_energy,
    ]

    #############################################

    # get the absolute path of the directory where the script is located
    script_dir = Path(__file__).resolve().parent

    # check if all relevant files are present in the script directory
    # if not, print warning and exit
    files = [
        script_dir / "../runscripts/run-cp2k-noctua2.sh",
        script_dir / "../runscripts/run-cp2k-bonna.sh",
    ]
    # resolve '..' parts to absolute paths
    files = [f.resolve() for f in files]

    for file_path in files:
        if not file_path.is_file():
            sys.exit(
                f" *** Warning: Input file '{file_path}' does not exist. Reinstall this setup tool. Exiting."
            )

    # get the abs path of the directory from which the script is called
    start_dir = os.getcwd()

    #############################################
    # setting up the calculation
    # depending on the type of calculation, different input files are needed

    if args["type"] in ["aimd", "energy", "adapt-sampl", "geoopt"]:
        # generate a project directory
        make_project_dir(project_dir, args["overwrite"])

        # change to the project directory and copy coords
        os.chdir(project_dir)
        shutil.copy(abs_coord, project_dir)
        # copy velocities if given
        if args["velocity"] is not None:
            shutil.copy(abs_velocity, project_dir)

        # copy run script and data files to the project directory
        cp_runscript(
            data=args,
            template_dir=script_dir,
            project_dir=project_dir,
        )

        # generate input files from snippets
        generate_input_files(data=args)

        # in the end, change back to the directory from which the script was called
        os.chdir(start_dir)

    elif args["type"] == "bqb":
        # generate a project directory
        make_project_dir(project_dir, args["overwrite"])

        # change to the project directory and copy coords
        os.chdir(project_dir)

        # generate subdirectories for the bqb jobs
        for i in range(args["n_bqb"]):
            bqb_path = Path("bqb_" + f"{i+1:02d}")
            bqb_path.mkdir(parents=True, exist_ok=True)
            shutil.copy(abs_coord, bqb_path)
            shutil.copy(abs_velocity, bqb_path)
            shutil.copy(abs_reftraj, bqb_path)
            os.chdir(bqb_path)
            cp_runscript(
                data=args,
                template_dir=script_dir,
                project_dir=Path("."),
                bqb_count=i,
            )
            generate_input_files(data=args, bqb_count=i)
            os.chdir("..")

        # in the end, change back to the directory from which the script was called
        os.chdir(start_dir)

    # print a message that the script has finished
    # print(type(args["project"]), type(project_dir))
    print("Finished setting up the project '" + args["project"] + "' .")

    return 0
