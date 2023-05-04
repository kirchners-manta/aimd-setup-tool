#!/usr/bin/python3

# Script to setup an AIMD simualtion with CP2K
# Written by Tom Frömbgen
# Last modified 2023-01-23

#############################################

# import modules
import sys
import argparse
import os
from pathlib import Path

# import routines
import routines

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
        print("Project directory '" + project_directory +
              "' already exists. Shall is be overwritten? [y/n]")
        answer = input()
        if answer in ["y", "Y", "j", "J"]:
            os.system("rm -rf " + project_directory)
            print("Overwriting old project directory '" +
                  project_directory + "'.\n")
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

#############################################


# define command line arguments
parser = argparse.ArgumentParser(prog="aimd-setup.py",
                                 description="Script to setup an AIMD simualtion with CP2K",
                                 epilog="Written for the Kirchner group by Tom Frömbgen. Internal use only.",
                                 add_help=True)

parser.add_argument("-p", type=str, metavar="PROJECT_NAME",
                    help="project name", required=True, dest="project",)

parser.add_argument("-b", type=str, metavar="BASIS_SET",
                    help="basis set", default="DZVP", dest="basis",
                    choices=["svz", "dzvp", "tzvp", "tzv2p", "tzv2px"])

parser.add_argument("-c", type=str, metavar="COORD_FILE", dest="coord",
                    help="coordinate file (xyz format)", default="input.xyz",)

parser.add_argument("--e-conv", type=float, metavar="CUTOFF",
                    dest="e_conv", help="energy convergence criterion in Hartree", default=1.0e-6)

parser.add_argument("-f", type=str, metavar="FUNCTIONAL",
                    help="density functional", default="BLYP", dest="func",
                    choices=["blyp", "bp", "pade", "pbe", "revpbe"])

parser.add_argument("--n-bqb", type=int, metavar="N",
                    help="number of bqb files to generate", default=6,
                    dest="n_bqb",)

parser.add_argument("--no-copy",
                    help="do not trajectory file to project directory",
                    action="store_true", default=False, dest="no_copy",)

parser.add_argument("-o", help="overwrite existing files",
                    action="store_true", default=False, dest="overwrite",)

parser.add_argument("-q", type=str, metavar="QUEUE",
                    help="queue to submit the job to", default="hedy", dest="queue", choices=["hedy", "iris", "noctua2"])

parser.add_argument("--reftraj", type=str, metavar="FILE",
                    help="reference trajectory file to calculate the spectrum from",
                    dest="reftraj")

parser.add_argument("-s", type=float, dest="boxsize",
                    help="box edge length in Angstrom", metavar="LENGTH", default=10.0)

parser.add_argument("--start-from", type=int, metavar="N",
                    help="start processing trajectory from step N",
                    default=1, dest="start_from",)

parser.add_argument("--spec", type=str, metavar="SPECTRUM",
                    dest="spectrum", help="spectrum to calculate", default="ir",
                    choices=["ir", "vcd", "raman", "roa"],)

parser.add_argument("--steps-bqb", type=int, metavar="N",
                    help="number of steps per bqb file (without overlap)", default=10000,
                    dest="steps_bqb",)

parser.add_argument("--steps-equi", type=int, metavar="N",
                    help="number of equilibration steps", default=20000)

parser.add_argument("--steps-relax", type=int, metavar="N",
                    help="number of relaxation steps", default=10000)

parser.add_argument("--steps-prod", type=int, metavar="N",
                    help="number of production steps", default=60000)

parser.add_argument("-t", type=str, metavar="JOB_TYPE",
                    help="type of calculation to perform", dest="type",
                    choices=["aimd", "bqb", "single-point"], default="aimd",)

parser.add_argument("--thermo", type=str, metavar="THERMO",
                    help="thermostat", default="nose",
                    choices=["nose", "csvr"])

parser.add_argument("--t-equi", type=float, metavar="TEMP",
                    help="equilibration temperature in K", default=400.0)

parser.add_argument("--t-relax", type=float, metavar="TEMP",
                    help="relaxation temperature in K", default=350.0)

parser.add_argument("--t-prod", type=float, metavar="TEMP",
                    help="production temperature in K", default=350.0)

parser.add_argument("-w", help="calculate Wannier functions in production run",
                    default=False, action="store_true", dest="wannier",)


# parse arguments
args = parser.parse_args()

# print help if no arguments are given
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

# capitalize the functional
args.func = args.func.upper()
# if REVPBE, use PBE for the pseudopotential, because CP2K does not have a REVPBE pseudopotential
if args.func == "REVPBE":
    pp_func = "PBE"
else:
    pp_func = args.func

# capitalize the basis set
# if a cardinal number > 2 is given, print warning
if args.basis in ["tzvp", "tzv2p", "tzv2px", ]:
    print(" *** Warning: basis set '" + args.basis +
          "' is valid, but not available in the short range form. This may lead to drastically increased computation time.\n")
    args.basis = args.basis + "-MOLOPT-GTH"
else:
    args.basis = args.basis + "-MOLOPT-SR-GTH"

# capitalize the thermostat
args.thermo = args.thermo.upper()

# runscript name
runscript_name = "run-cp2k-" + args.queue + ".sh"

# project path
project_dir = os.path.abspath(args.project)
args.project = os.path.basename(args.project)

# get absolute path of the coordinate file
abs_coord = os.path.abspath(args.coord)

# get basename of the coordinate file
args.coord = os.path.basename(abs_coord)

# if no reference trajectory is given, use project name
if args.reftraj is None:
    args.reftraj = args.project + "-pos-1.xyz"

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
files = [script_dir + "/input/bqb.inp",
         script_dir + "/input/geoopt.inp",
         script_dir + "/input/eq.inp",
         script_dir + "/input/relax.inp",
         script_dir + "/input/prod.inp",
         script_dir + "/input/single-point.inp",
         script_dir + "/data/BASIS_MOLOPT",
         script_dir + "/data/GTH_POTENTIALS",
         script_dir + "/data/dftd3.dat",
         script_dir + "/execute/run-cp2k-hedy.sh",
         script_dir + "/execute/run-cp2k-iris.sh",
         script_dir + "/execute/run-cp2k-noctua2.sh", ]
for f in files:
    if not os.path.isfile(f):
        sys.exit(" *** Warning: Input file '" + f +
                 "' does not exist. Reinstall this setup tool. Exiting.")

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

    # check if the coordinate file exists
    # if yes, copy it to the project directory
    if os.path.isfile(abs_coord):
        os.system("cp " + abs_coord + " .")
    # print warning if not
    else:
        print(" *** Warning: coordinate file '" +
              abs_coord + "' does not exist.")
        print("     This will cause an error in CP2K if you do not add it afterwards.\n")

    # define the input files
    cp2k_infiles_templates = [script_dir + "/input/geoopt.inp",
                              script_dir + "/input/eq.inp",
                              script_dir + "/input/relax.inp",
                              script_dir + "/input/prod.inp", ]

    # copy the template files to the project directory
    for f in cp2k_infiles_templates:
        os.system("cp " + f + " .")

    # get a list with the input files in the project directory
    cp2k_infiles = [project_dir + "/geoopt.inp",
                    project_dir + "/eq.inp",
                    project_dir + "/relax.inp",
                    project_dir + "/prod.inp", ]

    # adjust the input files
    routines.adjust_cp2k_input_aimd(cp2k_infiles=cp2k_infiles,
                                    data=args_dict)

    # copy run script and data files to the project directory
    routines.copy_cp2k_data_and_runscript(
        template_dir=script_dir,
        project_dir=project_dir,
        runscript=runscript_name)

    # adjust the job name in the run script
    routines.adjust_runscript(runscript=runscript_name,
                              project=args.project,
                              queue=args.queue,)

    # copy the cp2k data files to the project directory
    # os.system("cp " + script_dir + "/data/* .")

    # in the end, change back to the directory from which the script was called
    os.chdir(start_dir)

# BQB
elif args.type == "bqb":

    # generate a project directory
    make_project_dir(project_dir, args.overwrite)

    # change to the project directory
    os.chdir(project_dir)

    # check if the coordinate file exists
    # if yes, copy it to the project directory
    if os.path.isfile(abs_coord):
        os.system("cp " + abs_coord + " .")
    # print warning if not
    else:
        print(" *** Warning: coordinate file '" +
              abs_coord + "' does not exist.")
        print("     This will cause an error in CP2K if you do not add it afterwards.\n")

    # define the input files
    cp2k_infiles_templates = [script_dir + "/input/bqb.inp", ]

    # copy the template files to the project directory
    for f in cp2k_infiles_templates:
        os.system("cp " + f + " .")

    # get a list with the input files in the project directory
    cp2k_infiles = getFileList(project_dir, "*.inp")

    # adjust the input files
    routines.adjust_cp2k_input_bqb(cp2k_infiles=cp2k_infiles,
                                   data=args_dict,
                                   project=args.project,
                                   runscript_name=runscript_name,
                                   queue=args.queue,
                                   template_dir=script_dir,)

    # check if the trajectory file exists
    # if yes, copy it to the project directory
    if os.path.isfile(abs_reftraj):
        print("Copying reference trajectory to bqbs...\n")
        os.system(
            "for dir in $(ls -d bqb_[1-9]*); do cp " + abs_reftraj + " $dir; done")
    # print warning if not
    else:
        print(" *** Warning: trajectory file '" +
              abs_reftraj + "' does not exist.")
        print("     This will cause an error in CP2K if you do not add it afterwards.\n")

    # in the end, change back to the directory from which the script was called
    os.chdir(start_dir)

# single-point
elif args.type == "single-point":

    # generate a project directory
    make_project_dir(project_dir, args.overwrite)

    # change to the project directory
    os.chdir(project_dir)

    # check if the coordinate file exists
    # if yes, copy it to the project directory
    if os.path.isfile(abs_coord):
        os.system("cp " + abs_coord + " .")
        # then, check if the coordinate file has two lines before the first atom
        # if yes, remove the first two lines
        with open(args.coord, "r") as f:
            lines = f.readlines()
            # if the first entry in the first line is a number, the file has two lines before the first atom
            if lines[0].split()[0].isdigit():
                # remove the first two lines
                lines = lines[2:]
                # write the new file
                with open(args.coord, "w") as f:
                    f.writelines(lines)

    # print warning if not
    else:
        print(" *** Warning: coordinate file '" +
              abs_coord + "' does not exist.")
        print("     This will cause an error in CP2K if you do not add it afterwards.\n")

    # define the input files
    cp2k_infiles_templates = [script_dir + "/input/single-point.inp", ]

    # copy the template files to the project directory
    for f in cp2k_infiles_templates:
        os.system("cp " + f + " .")

    # get a list with the input files in the project directory
    cp2k_infiles = [project_dir + "/single-point.inp", ]

    # adjust the input files
    routines.adjust_cp2k_input_sp(cp2k_infiles=cp2k_infiles,
                                  data=args_dict,)

    # copy run script and data files to the project directory
    routines.copy_cp2k_data_and_runscript(
        template_dir=script_dir,
        project_dir=project_dir,
        runscript=runscript_name)

    # adjust the job name in the run script
    routines.adjust_runscript(runscript=runscript_name,
                              project=args.project,
                              queue=args.queue,)

    # in the end, change back to the directory from which the script was called
    os.chdir(start_dir)

# print a message that the script has finished
print("Finished setting up the project '" +
      args.project + "' in " + project_dir + " .")
