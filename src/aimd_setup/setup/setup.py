"""
Main setup script for AIMD setup package.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np

from ..adjust_input import cp_runscript
from ..functions import make_project_dir
from ..snippets import generate_input_files

# import toml


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

    # debug
    # print dictionary with arguments to .toml file
    # with open("config.toml", "w", encoding="utf-8") as f:
    #     toml.dump(args, f)

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

    # seed
    if args["random_seed"]:
        args["seed"] = np.random.randint(1, 1000000)

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
    print("\nThe following arguments were given (including defaults):")
    print(f"{'Project name:'.ljust(40)}{args['project']}")
    print(f"{'Box size [Angstrom]:'.ljust(40)}{args['boxsize']}")
    print(f"{'Periodic boundary conditions:'.ljust(40)}{args['pbc'].upper()}")
    print(f"{'Coordinate file:'.ljust(40)}{args['coord']}")
    print(f"{'Charge:'.ljust(40)}{args['charge']}")
    if args["uks"]:
        print(
            f"{'Multiplicity:'.ljust(40)}{args['mult']} (open shell calculation)"
        )
    else:
        print(f"{'Multiplicity:'.ljust(40)}{args['mult']}")
    print(f"{'Seed:'.ljust(40)}{args['seed']}")
    print(f"{'QS method:'.ljust(40)}{qs_method}")
    if qs_method == "GPW":
        print(f"{'Density functional:'.ljust(40)}{args['func'].upper()}")
        print(f"{'Pseudopotential:'.ljust(40)}{pp_func}")
        print(f"{'Basis set:'.ljust(40)}{args['basis']}")
        if args["dftu"] is not None:
            print(
                f"{'DFT+U:'.ljust(40)}",
                [
                    f"{k}: L={v[0]}, U-J={v[1]} eV"
                    for k, v in args["dftu"].items()
                ],
            )
        print(f"{'Grids:'.ljust(40)}{args['grid_n']}")
        print(f"{'Grids cutoff [Ry]:'.ljust(40)}{args['grid_cutoff']}")
        print(f"{'Grids rel cutoff [Ry]:'.ljust(40)}{args['grid_rel_cutoff']}")

    # arguments that are only needed for a certain type of calculation are printed last
    if args["type"] == "aimd":
        # define which jobs are to be executed
        exec_geoopt = False
        exec_eq = not args["no_equi"]
        exec_relax = not args["no_relax"]
        exec_prod = not args["no_prod"]
        exec_bqb = False
        exec_energy = False

        print(f"{'Type of calculation:'.ljust(40)}AIMD simulation")
        print(f"{'Timestep [fs]:'.ljust(40)}{args['timestep']}")
        if not args["no_equi"]:
            print(f"{'Equilibration steps:'.ljust(40)}{args['steps_equi']}")
            print(
                f"{'Equilibration temperature [K]:'.ljust(40)}{args['t_equi']}"
            )
        if not args["no_relax"]:
            print(f"{'Relaxation steps:'.ljust(40)}{args['steps_relax']}")
            print(
                f"{'Relaxation temperature [K]:'.ljust(40)}{args['t_relax']}"
            )
        if not args["no_prod"]:
            print(f"{'Production steps:'.ljust(40)}{args['steps_prod']}")
            print(f"{'Production temperature [K]:'.ljust(40)}{args['t_prod']}")
        if not args["no_equi"]:
            print(f"{'Ensemble in equilibration:'.ljust(40)}NVT")
            print(f"{'Thermostat:'.ljust(40)}{args['thermo']}")
        if not args["no_prod"]:
            print(f"{'Ensemble in production:'.ljust(40)}{args['ensemble']}")
            print(f"{'Thermostat:'.ljust(40)}{args['thermo']}")
        if args["velocity"] is not None:
            print(f"{'Initial velocities:'.ljust(40)}{args['velocity']}")
        if args["bqb"]:
            print(
                f"{'Print BQB file every [steps]:'.ljust(40)}{args['print_bqb_every']}"
            )
        if args["cube"]:
            print(
                f"{'Print cube file every [steps]:'.ljust(40)}{args['print_cube_every']}"
            )
        if args["voronoi"]:
            print(
                f"{'Print Voronoi file every [steps]:'.ljust(40)}{args['print_voronoi_every']}"
            )
        if args["wannier"]:
            print(
                f"{'Wannier localization every [steps]:'.ljust(40)}{args['print_wannier_every']}"
            )

    elif args["type"] == "bqb":
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = True
        exec_energy = False

        print(f"{'Type of calculation:'.ljust(40)}BQB file production")
        print(f"{'Reference trajectory:'.ljust(40)}{args['reftraj']}")
        print(
            f"{'Process Trajectory from step:'.ljust(40)}{args['start_from']}"
        )
        print(f"{'Bqb files:'.ljust(40)}{args['n_bqb']}")
        print(f"{'Steps per bqb file:'.ljust(40)}{args['steps_bqb']}")
        print(f"{'Spectrum:'.ljust(40)}{args['spectrum']}")

    elif args["type"] == "energy":
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = False
        exec_energy = True

        print(
            f"{'Type of calculation:'.ljust(40)}Single point energy calculation"
        )
        print(f"{'Energy convergence [Hartree]:'.ljust(40)}{args['e_conv']}")

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

        print(f"{'Type of calculation:'.ljust(40)}Adaptive sampling")
        print(f"{'Production steps:'.ljust(40)}{args['steps_prod']}")
        print(f"{'Production temperature [K]:'.ljust(40)}{args['t_prod']}")
        print(f"{'Print BQB file:'.ljust(40)}{args['bqb']}")

    elif args["type"] == "geoopt":
        exec_geoopt = True
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = False
        exec_energy = False

        print(f"{'Type of calculation:'.ljust(40)}Geometry optimization")
        print(f"{'Convergence criteria:'.ljust(40)}{args['opt_level']}")

    # electric field settings
    if args["efield"] is not None:
        print(f"{'Periodic E-field:'.ljust(40)}{args['efield']}")
        print(
            f"{'E-field strength [a.u.]:'.ljust(40)}{args['efield_strength']}"
        )

    # HPC information
    print(f"{'CP2K version:'.ljust(40)}{args['cp2k_version']}")
    print(f"{'Queue:'.ljust(40)}{args['queue']}")
    print(f"{'Runscript:'.ljust(40)}{runscript_name}")
    print(f"{'CPU cores:'.ljust(40)}{args['cpu']}")
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

            # copy velocities if given
            if args["velocity"] is not None:
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
