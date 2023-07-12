# AIMD setup tool
#
# This python program sets up calculations with CP2K.
# It is mainly designed for AIMD simulations and the subsequent calculation vibrational spectra.
# Further functionality is planned.
# The program creates a project directory, copies the input files, adjusts them to the given parameters,
# and creates a runscript to submit the calculation to the cluster.
#
# This program is developed by Tom Frömbgen, (Group of Prof. Dr. Barbara Kirchner, University of Bonn, Germany) and maily designed for the use in this group.
# It is published under the MIT license.

#############################################

from __future__ import annotations

import os
import sys
from pathlib import Path

import adjust_input_files  # to adjust the cp2k input files
import argparser  # custom argument parser


# define useful functions
def getFileList(path: str, regex: str) -> list:
    """Get a list of files in a directory.

    Parameters
    ----------
    path : str
        path to the directory where the files are located
    regex : str
        regular expression to filter the files

    Returns
    -------
    list
        list of posix paths to the files
    """
    filelist = []
    for file in sorted(Path(path).rglob(regex)):
        filelist.append(file)

    if len(filelist) == 0:
        sys.exit("No '*data' files found.")

    return filelist


def make_project_dir(project_directory: str, overwrite: bool) -> None:
    """Create a project directory. Check if the project directory exists; if yes, ask if it should be overwritten; if no, create it

    Parameters
    ----------
    project_directory : str
        path to the project directory
    overwrite : bool
        if True, overwrite existing project directory
    """

    if os.path.isdir(project_directory) and not overwrite:
        print(
            "Project directory '"
            + project_directory
            + "' already exists. Shall is be overwritten? [y/n]"
        )
        answer = input()
        if answer in ["y", "Y", "j", "J"]:
            os.system("rm -rf " + project_directory)
            print("Overwriting old project directory '" + project_directory + "'.\n")
            os.system("mkdir " + project_directory)
        else:
            sys.exit("Project directory not overwritten. Exiting.\n")
    elif os.path.isdir(project_directory) and overwrite:
        os.system("rm -rf " + project_directory)
        print("Overwriting old project directory '" + project_directory + "'.\n")
        os.system("mkdir " + project_directory)
    else:
        print("Creating new project directory '" + project_directory + "'.\n")
        os.system("mkdir " + project_directory)


# parse arguments to make them available in the script
args = argparser.parser().parse_args()

# capitalize the functional
args.func = args.func.upper()
# if REVPBE, use PBE for the pseudopotential, because CP2K does not have a REVPBE pseudopotential
if args.func == "REVPBE":
    pp_func = "PBE"
# otherwise, use the functional for the pseudopotential
else:
    pp_func = args.func

# capitalize the basis set
# if a cardinal number > 2 is given, print warning
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
    print("Calculate Wannier functions:", args.wannier)

elif args.type == "bqb":
    print("Reference trajectory:", args.reftraj)
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
    script_dir + "/input/bqb.inp",
    script_dir + "/input/geoopt.inp",
    script_dir + "/input/eq.inp",
    script_dir + "/input/relax.inp",
    script_dir + "/input/prod.inp",
    # script_dir + "/input/single-point.inp",
    script_dir + "/data/BASIS_MOLOPT",
    script_dir + "/data/GTH_POTENTIALS",
    script_dir + "/data/dftd3.dat",
    script_dir + "/execute/run-cp2k-aimd-hedy.sh",
    script_dir + "/execute/run-cp2k-aimd-iris.sh",
    script_dir + "/execute/run-cp2k-aimd-noctua2.sh",
    script_dir + "/execute/run-cp2k-bqb-hedy.sh",
    script_dir + "/execute/run-cp2k-bqb-iris.sh",
    script_dir + "/execute/run-cp2k-bqb-noctua2.sh",
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
        script_dir + "/input/geoopt.inp",
        script_dir + "/input/eq.inp",
        script_dir + "/input/relax.inp",
        script_dir + "/input/prod.inp",
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
    adjust_input_files.adjust_cp2k_input_aimd(cp2k_infiles=cp2k_infiles, data=args_dict)

    # copy run script and data files to the project directory
    adjust_input_files.copy_cp2k_data_and_runscript(
        template_dir=script_dir,
        project_dir=project_dir,
        runscript=runscript_name,
    )

    # adjust the job name in the run script
    adjust_input_files.adjust_runscript(
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
        script_dir + "/input/bqb.inp",
    ]

    # copy the template files to the project directory
    for f in cp2k_infiles_templates:
        os.system("cp " + f + " .")

    # get a list with the input files in the project directory
    cp2k_infiles = getFileList(project_dir, "*.inp")

    # adjust the input files
    adjust_input_files.adjust_cp2k_input_bqb(
        cp2k_infiles=cp2k_infiles,
        data=args_dict,
        project=args.project,
        runscript_name=runscript_name,
        queue=args.queue,
        template_dir=script_dir,
    )

    # copy the coordinates and trajectory files to the project directory
    print("Copying coordinates and reference trajectory to bqbs...\n")

    os.system(
        "for dir in $(ls -d bqb_*[0-9]); do cp "
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
print("Finished setting up the project '" + args.project + "' in " + project_dir + " .")
