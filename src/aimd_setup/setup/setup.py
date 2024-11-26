"""
Main setup script for AIMD setup package.
"""

from __future__ import annotations

import argparse
import os
import sys

from ..adjust_input import cp_runscript
from ..functions import make_project_dir
from ..snippets import generate_input_files


def setup_job(args: argparse.Namespace) -> int:
    # if REVPBE, use PBE for the pseudopotential, because CP2K does not have a REVPBE pseudopotential
    if args.func == "revpbe":
        pp_func = "PBE"
    # if R2SCAN, use SCAN for the pseudopotential, because CP2K does not have a R2SCAN pseudopotential
    elif args.func == "r2scan":
        pp_func = "SCAN"
    # otherwise, use the functional for the pseudopotential
    else:
        pp_func = args.func.upper()

    # if xTB is chosen, the QS method is xTB, else GPW
    if args.func == "xtb":
        qs_method = "XTB"
    else:
        qs_method = "GPW"

    # capitalize the basis set
    # if a cardinal number < 2, use SR-GTH
    if args.basis in ["tzvp", "tzv2p", "tzv2px"]:
        args.basis = args.basis.upper() + "-MOLOPT-GTH"
    else:
        args.basis = args.basis.upper() + "-MOLOPT-SR-GTH"

    # capitalize the thermostat
    args.thermo = args.thermo.upper()

    # capitalize the ensemble
    args.ensemble = args.ensemble.upper()

    # runscript name
    runscript_name = "run-cp2k-" + args.queue + ".sh"

    # project path
    project_dir = os.path.abspath(args.project)
    args.project = os.path.basename(args.project)

    # get absolute path of the coordinate file
    abs_coord = os.path.abspath(args.coord)

    # get basename of the coordinate file
    args.coord = os.path.basename(abs_coord)

    # if bqb calculation, get absolute path of the reference trajectory file
    if args.type == "bqb":
        # get absolute path of the reference trajectory file
        abs_reftraj = os.path.abspath(args.reftraj)

        # get basename of the reference trajectory file
        args.reftraj = os.path.basename(abs_reftraj)

    # check given box dimensions
    # if only one is given -> cubic box, set all box dimensions to the same value
    if type(args.boxsize) == float:
        args.boxsize = (
            str(args.boxsize) + " " + str(args.boxsize) + " " + str(args.boxsize)
        )
    # if three are given -> orthorhombic boxsize
    elif len(args.boxsize) == 3:
        args.boxsize = " ".join([str(x) for x in args.boxsize])
    else:
        sys.exit(
            "Invalid box dimensions. Provide either one (cubic) or three (orthorhombic) box lengths."
        )

    # if velocity is given, no geometry optimization is performed
    if args.velocity is not None:
        args.no_geoopt = True
        abs_velocity = os.path.abspath(args.velocity)
        args.velocity = os.path.basename(abs_velocity)

    # print the arguments relevant for the type of calculation
    print("The following arguments were given (including defaults):")

    # arguments that are always needed, printed first
    print("Project name:", args.project)
    print("Job type:", args.type)
    print("Box size [Angstrom]:", args.boxsize)
    print("Coordinate file:", args.coord)
    print("QS method:", qs_method)
    if qs_method == "GPW":
        print("Density functional:", args.func.upper())
        print("Pseudopotential:", pp_func)
        print("Basis set:", args.basis)

    # arguments that are only needed for a certain type of calculation are printed last
    if args.type == "aimd":
        # set variables for which jobs to execute
        exec_geoopt = not args.no_geoopt
        exec_eq = not args.no_equi
        exec_relax = not args.no_relax
        exec_prod = not args.no_prod
        exec_bqb = False
        exec_energy = False

        # print the relevant arguments
        if not args.no_equi:
            print("Equilibration steps:", args.steps_equi)
            print("Equilibration temperature [K]:", args.t_equi)
        if not args.no_relax:
            print("Relaxation steps:", args.steps_relax)
            print("Relaxation temperature [K]:", args.t_relax)
        if not args.no_prod:
            print("Production steps:", args.steps_prod)
            print("Production temperature [K]:", args.t_prod)
        if not args.no_equi:
            print("Thermodynamic ensemble in equilibration:", "NVT")
            print("Thermostat:", args.thermo)
        if not args.no_prod:
            print("Thermodynamic ensemble in production:", args.ensemble)
            print("Thermostat:", args.thermo)
        if args.velocity is not None:
            print("Initial velocities:", args.velocity)
        print("Print BQB file:", args.bqb)
        print("Calculate Wannier functions:", args.wannier)

    elif args.type == "bqb":
        # set variables for which jobs to execute
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = True
        exec_energy = False

        # print the relevant arguments
        print("Reference trajectory:", args.reftraj)
        print("Process Trajectory from step:", args.start_from)
        print("Bqb files:", args.n_bqb)
        print("Steps per bqb file:", args.steps_bqb)
        print("Spectrum:", args.spectrum)

    elif args.type == "energy":
        # set variables for which jobs to execute
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = False
        exec_bqb = False
        exec_energy = True

        # print the relevant arguments
        print("Energy convergence criterion [Hartree]:", args.e_conv)

    elif args.type == "adapt-sampl":
        exec_geoopt = False
        exec_eq = False
        exec_relax = False
        exec_prod = True
        exec_bqb = False
        exec_energy = False

        # set extra arguments specific to this type of calculation
        args.steps_prod = 2
        args.bqb = True
        # velocity is required
        if args.velocity is None:
            sys.exit(
                " *** Velocity file is required for adaptive sampling. Watch the velocity format. Exiting."
            )

        print("Production steps:", args.steps_prod)
        print("Production temperature [K]:", args.t_prod)
        print("Print BQB file:", args.bqb)

    print("Queue:", args.queue)
    print("Runscript:", runscript_name)
    print("CPU cores:", args.cpu)
    print("")

    # which jobs to execute
    jobs_to_exec = [
        exec_geoopt,
        exec_eq,
        exec_relax,
        exec_prod,
        exec_bqb,
        exec_energy,
    ]

    # create a dictionary with the arguments
    args_dict = vars(args)
    args_dict["pp_func"] = pp_func
    args_dict["joblist"] = jobs_to_exec
    args_dict["runscript"] = runscript_name
    args_dict["qs_method"] = qs_method

    # adjust bqb history parameter if necessary
    if (
        (args.type == "bqb" and args.steps_bqb < 10)
        or args.type == "adapt-sampl"
        or (args.type == "aimd" and args.bqb and args.steps_prod < 10)
    ):
        args_dict["bqb_history"] = 1
    else:
        args_dict["bqb_history"] = 10

    #############################################

    # get the absolute path of the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # check if all relevant files are present in the script directory
    # if not, print warning and exit
    files = [
        script_dir + "/../runscripts/run-cp2k-noctua2.sh",
        script_dir + "/../runscripts/run-cp2k-bonna.sh",
    ]
    for f in files:
        if not os.path.isfile(f):
            sys.exit(
                " *** Warning: Input file '"
                + f
                + "' does not exist. Reinstall this setup tool. Exiting."
            )

    # get the abs path of the directory from which the script is called
    start_dir = os.getcwd()

    #############################################
    # setting up the calculation
    # depending on the type of calculation, different input files are needed

    if args.type in ["aimd", "energy", "adapt-sampl"]:
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory and copy coords
        os.chdir(project_dir)
        os.system("cp " + abs_coord + " .")
        # copy velocities if given
        if args.velocity is not None:
            os.system("cp " + abs_velocity + " .")

        # copy run script and data files to the project directory
        cp_runscript(
            data=args_dict,
            template_dir=script_dir,
            project_dir=project_dir,
        )

        # generate input files from snippets
        generate_input_files(data=args_dict)

        # in the end, change back to the directory from which the script was called
        os.chdir(start_dir)

    elif args.type == "bqb":
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory and copy coords
        os.chdir(project_dir)

        # generate subdirectories for the bqb jobs
        for i in range(args.n_bqb):
            os.mkdir("bqb_" + str(i + 1))
            os.system("cp " + abs_coord + " bqb_" + str(i + 1) + "/")
            os.system("cp " + abs_reftraj + " bqb_" + str(i + 1) + "/")
            os.chdir("bqb_" + str(i + 1))
            cp_runscript(
                data=args_dict,
                template_dir=script_dir,
                project_dir=".",
            )
            generate_input_files(data=args_dict, bqb_count=i)
            os.chdir("..")

        # in the end, change back to the directory from which the script was called
        os.chdir(start_dir)

    # print a message that the script has finished
    print(
        "Finished setting up the project '"
        + args.project
        + "' in "
        + project_dir
        + " ."
    )

    return 0
