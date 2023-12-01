"""
Main setup script for AIMD setup package.
"""

from __future__ import annotations

import argparse
import os
import sys

from ..adjust_input import (
    adjust_cp2k_input_aimd,
    adjust_cp2k_input_bqb,
    adjust_runscript,
    copy_cp2k_data_and_runscript,
)
from ..functions import getFileList, make_project_dir


def setup_job(args: argparse.Namespace) -> int:
    # capitalize the functional
    args.func = args.func.upper()
    # if REVPBE, use PBE for the pseudopotential, because CP2K does not have a REVPBE pseudopotential
    if args.func == "REVPBE":
        pp_func = "PBE"
    # otherwise, use the functional for the pseudopotential
    else:
        pp_func = args.func

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
    runscript_name = "run-cp2k-" + args.type + "-" + args.queue + ".sh"

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

    # print the arguments relevant for the type of calculation
    print("The following arguments were given (including defaults):")

    # arguments that are always needed, printed first
    print("Project name:", args.project)
    print("Job type:", args.type)
    print("Box size [Angstrom]:", args.boxsize)
    print("Coordinate file:", args.coord)
    print("Density functional:", args.func)
    print("Pseudopotential:", pp_func)
    print("Basis set:", args.basis)

    # arguments that are only needed for a certain type of calculation are printed last
    if args.type == "aimd":
        print("Thermostat:", args.thermo)
        print("Equilibration temperature [K]:", args.t_equi)
        print("Relaxation temperature [K]:", args.t_relax)
        print("Production temperature [K]:", args.t_prod)
        print("Equilibration steps:", args.steps_equi)
        print("Relaxation steps:", args.steps_relax)
        print("Production steps:", args.steps_prod)
        print("Thermodynamic ensemble in equilibration:", "NVT")
        print("Thermodynamic ensemble in production:", args.ensemble)
        print("Print BQB file:", args.bqb_in_prod)
        print("Calculate Wannier functions:", args.wannier)

    elif args.type == "bqb":
        print("Reference trajectory:", args.reftraj)
        print("Process Trajectory from step:", args.start_from)
        print("Bqb files:", args.n_bqb)
        print("Steps per bqb file:", args.steps_bqb)
        print("Spectrum:", args.spectrum)

    elif args.type == "single-point":
        print("Energy convergence criterion [Hartree]:", args.e_conv)

    print("Queue:", args.queue)
    print("Runscript:", runscript_name)
    print("")

    # create a dictionary with the arguments and add pp_func
    args_dict = vars(args)
    args_dict["pp_func"] = pp_func

    #############################################

    # get the absolute path of the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # check if all relevant files are present in the script directory
    # if not, print warning and exit
    files = [
        script_dir + "/../cp2k-input/bqb.inp",
        script_dir + "/../cp2k-input/geoopt.inp",
        script_dir + "/../cp2k-input/eq.inp",
        script_dir + "/../cp2k-input/relax.inp",
        script_dir + "/../cp2k-input/prod.inp",
        # script_dir + "/../cp2k-input/single-point.inp",
        script_dir + "/../cp2k-datafiles/BASIS_MOLOPT",
        script_dir + "/../cp2k-datafiles/GTH_POTENTIALS",
        script_dir + "/../cp2k-datafiles/dftd3.dat",
        script_dir + "/../runscripts/run-cp2k-aimd-hedy.sh",
        script_dir + "/../runscripts/run-cp2k-aimd-iris.sh",
        script_dir + "/../runscripts/run-cp2k-aimd-noctua2.sh",
        script_dir + "/../runscripts/run-cp2k-bqb-hedy.sh",
        script_dir + "/../runscripts/run-cp2k-bqb-iris.sh",
        script_dir + "/../runscripts/run-cp2k-bqb-noctua2.sh",
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

    # AIMD
    if args.type == "aimd":
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory
        os.chdir(project_dir)

        #  copy the coordinate to the project directory
        os.system("cp " + abs_coord + " .")

        # define the input files
        cp2k_infiles_templates = [
            script_dir + "/../cp2k-input/geoopt.inp",
            script_dir + "/../cp2k-input/eq.inp",
            script_dir + "/../cp2k-input/relax.inp",
            script_dir + "/../cp2k-input/prod.inp",
        ]

        # copy the template files to the project directory
        for f in cp2k_infiles_templates:
            os.system("cp " + f + " .")

        # get a list with the input files in the project directory
        cp2k_infiles = [
            project_dir + "/geoopt.inp",
            project_dir + "/eq.inp",
            project_dir + "/relax.inp",
            project_dir + "/prod.inp",
        ]

        # adjust the input files
        adjust_cp2k_input_aimd(cp2k_infiles=cp2k_infiles, data=args_dict)

        # copy run script and data files to the project directory
        copy_cp2k_data_and_runscript(
            template_dir=script_dir,
            project_dir=project_dir,
            runscript=runscript_name,
        )

        # adjust the job name in the run script
        adjust_runscript(
            runscript=runscript_name,
            project=args.project,
            queue=args.queue,
        )

        # in the end, change back to the directory from which the script was called
        os.chdir(start_dir)

    # BQB
    elif args.type == "bqb":
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory
        os.chdir(project_dir)

        # define the input files
        cp2k_infiles_templates = [
            script_dir + "/../cp2k-input/bqb.inp",
        ]

        # copy the template files to the project directory
        for f in cp2k_infiles_templates:
            os.system("cp " + f + " .")

        # get a list with the input files in the project directory
        cp2k_infiles = getFileList(project_dir, "*.inp")

        # adjust the input files
        adjust_cp2k_input_bqb(
            cp2k_infiles=cp2k_infiles,
            data=args_dict,
            runscript_name=runscript_name,
            queue=args.queue,
            template_dir=script_dir,
        )

        # copy the coordinates and trajectory files to the project directory
        print("Copying coordinates and reference trajectory to bqbs...\n")

        os.system(
            "for dir in $(ls -d bqb_*[0-9]*); do cp "
            + abs_reftraj
            + " $dir; cp "
            + abs_coord
            + " $dir; done"
        )

        # in the end, change back to the directory from which the script was called
        os.chdir(start_dir)

    # single-point
    elif args.type == "single-point":
        # print warning
        sys.exit("This feature is still under development.")

    # print a message that the script has finished
    print(
        "Finished setting up the project '"
        + args.project
        + "' in "
        + project_dir
        + " ."
    )

    return 0
