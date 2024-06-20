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
    adjust_cp2k_input_sp,
    adjust_runscript,
    copy_cp2k_data_and_runscript,
)
from ..snippets import generate_input_files
from ..functions import getFileList, make_project_dir


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
    if len(args.boxsize) == 1:
        args.boxsize = (
            str(args.boxsize[0])
            + " "
            + str(args.boxsize[0])
            + " "
            + str(args.boxsize[0])
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

    print("Queue:", args.queue)
    print("Runscript:", runscript_name)
    print("CPU cores:", args.cpu)
    print("")

    # create a dictionary with the arguments and add pp_func
    args_dict = vars(args)
    args_dict["pp_func"] = pp_func

    jobs_to_exec = [
        exec_geoopt,
        exec_eq,
        exec_relax,
        exec_prod,
        exec_bqb,
        exec_energy,
    ]

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
        script_dir + "/../cp2k-input/energy.inp",
        script_dir + "/../cp2k-datafiles/BASIS_MOLOPT",
        script_dir + "/../cp2k-datafiles/GTH_POTENTIALS",
        script_dir + "/../cp2k-datafiles/dftd3.dat",
        script_dir + "/../runscripts/run-cp2k-noctua2.sh",
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

    if args.type == "aimd" or args.type == "bqb" or args.type == "energy":
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory
        os.chdir(project_dir)

        #  copy the coordinate to the project directory
        os.system("cp " + abs_coord + " .")

        # copy velocities if given
        if args.velocity is not None:
            os.system("cp " + abs_velocity + " .")

        # generate input files from snippets
        generate_input_files(data=args_dict, joblist=jobs_to_exec)

    # AIMD
    elif args.type == "aimd":
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory
        os.chdir(project_dir)

        #  copy the coordinate to the project directory
        os.system("cp " + abs_coord + " .")

        # copy velocities if given
        if args.velocity is not None:
            os.system("cp " + abs_velocity + " .")

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
        adjust_cp2k_input_aimd(
            cp2k_infiles=cp2k_infiles, which_jobs=jobs_to_exec, data=args_dict
        )

        # remove the input files that are not needed
        for i, job in enumerate(jobs_to_exec):
            if not job:
                os.system("rm " + cp2k_infiles[i])

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
            ncpu=args.cpu,
            joblist=jobs_to_exec,
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
    elif args.type == "energy":
        # generate a project directory
        make_project_dir(project_dir, args.overwrite)

        # change to the project directory
        os.chdir(project_dir)

        # define the input files
        cp2k_infiles_templates = [
            script_dir + "/../cp2k-input/energy.inp",
        ]

        # copy the template files to the project directory
        for f in cp2k_infiles_templates:
            os.system("cp " + f + " .")

        # get a list with the input files in the project directory
        cp2k_infiles = getFileList(project_dir, "*.inp")

        #  copy the coordinate to the project directory
        os.system("cp " + abs_coord + " .")

        # adjust the input files
        adjust_cp2k_input_sp(
            cp2k_infiles=cp2k_infiles,
            data=args_dict,
        )

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

    # print a message that the script has finished
    print(
        "Finished setting up the project '"
        + args.project
        + "' in "
        + project_dir
        + " ."
    )

    return 0
