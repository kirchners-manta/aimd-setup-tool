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


# define command line arguments
parser = argparse.ArgumentParser(prog="aimd-setup.py",
                                 description="Script to setup an AIMD simualtion with CP2K",
                                 epilog="Written for the Kirchner group by Tom Frömbgen. Internal use only.",
                                 add_help=True)

parser.add_argument("-p", "--project", type=str, metavar="PROJECT_NAME",
                    help="project name", required=True,)
parser.add_argument("-b", "--boxsize", type=float,
                    help="box size in Angstrom", required=True,)
parser.add_argument("-c", "--coord", type=str, metavar="COORDINATE_FILE",
                    help="coordinate file (xyz format)", required=True,)
parser.add_argument("--thermo", type=str, metavar="THERMOSTAT",
                    help="thermostat", default="NOSE")
parser.add_argument("--t-equi", type=float, metavar="TEMPERATURE",
                    help="equilibration temperature in K", default=400.0)
parser.add_argument("--t-relax", type=float, metavar="TEMPERATURE",
                    help="relaxation temperature in K", default=350.0)
parser.add_argument("--t-prod", type=float, metavar="TEMPERATURE",
                    help="production temperature in K", default=350.0)
parser.add_argument("--steps-equi", type=int, metavar="N_STEPS",
                    help="number of equilibration steps", default=20000)
parser.add_argument("--steps-relax", type=int, metavar="N_STEPS",
                    help="number of relaxation steps", default=10000)
parser.add_argument("--steps-prod", type=int, metavar="N_STEPS",
                    help="number of production steps", default=60000)
parser.add_argument("--func", type=str, metavar="DENSITY_FUNCTIONAL",
                    help="density functional", default="BLYP")
parser.add_argument("--basis", type=str, metavar="BASIS_SET",
                    help="basis set", default="DZVP")
parser.add_argument("-w", "--wannier", help="calculate Wannier functions in production run",
                    default=False, action="store_true")

# parse arguments
args = parser.parse_args()

# print help if no arguments are given
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

# check if the project directory exists
# if yes, ask if it should be overwritten
# if no, create it
if os.path.isdir(args.project):
    print("Project directory '" + args.project +
          "' already exists. Shall is be overwritten? [y/n]")
    answer = input()
    if answer in ["y", "Y", "j", "J"]:
        os.system("rm -rf " + args.project)
        print("Creating project directory '" + args.project + "'.\n")
        os.system("mkdir " + args.project)
    else:
        sys.exit("Project directory not overwritten. Exiting.\n")
else:
    print("Creating project directory '" + args.project + "'.\n")
    os.system("mkdir " + args.project)

# check if a valid thermostat was given
# If yes, capitalize it
if args.thermo.upper() == "NOSE" or args.thermo.upper() == "CSVR":
    args.thermo = args.thermo.upper()
# else, print warning and exit
else:
    print(" *** Warning: thermostat '" + args.thermo + "' is not valid.")
    print("     Valid options are 'NOSE' (Nose-Hoover) and 'CSVR'.\n")
    sys.exit("")

# check if a valid density functional was given
# If yes, capitalize it
functionals = ["BLYP", "BP", "PADE", "PBE", "REVPBE"]
if args.func.upper() in functionals:
    args.func = args.func.upper()
    # if REVPBE, use PBE for the pseudopotential, because CP2K does not have a REVPBE pseudopotential
    if args.func == "REVPBE":
        pp_func = "PBE"
    # else use the given functional
    else:
        pp_func = args.func
# else, print warning and exit
else:
    print(" *** Warning: density functional '" + args.func + "' is not valid.")
    print("     Valid options are:")
    for f in functionals:
        print("     ", f)
    sys.exit("")

# check if a valid basis set was given
# If yes, capitalize it
basis_sets = ["SVZ", "DZVP", "TZVP", "TZV2P", "TZV2PX", ]
if args.basis.upper() in basis_sets:
    # if a cardinal number > 2 is given, print warning
    if args.basis.upper() in ["TZVP", "TZV2P", "TZV2PX", ]:
        print(" *** Warning: basis set '" + args.basis +
              "' is valid, but not available in the short range form. This may lead to drastically increased computation time.\n")
        args.basis = args.basis.upper() + "-MOLOPT-GTH"
    else:
        args.basis = args.basis.upper() + "-MOLOPT-SR-GTH"
# else, print warning and exit
else:
    print(" *** Warning: basis set '" + args.basis + "' is not valid.")
    print("     Valid options are:")
    for b in basis_sets:
        print("     ", b)
    sys.exit("")

# print the arguments
print("The following arguments were given (including defaults):")
print("Project name:", args.project)
print("Box size [Angstrom]:", args.boxsize)
print("Coordinate file:", args.coord)
print("Thermostat:", args.thermo)
print("Equilibration temperature [K]:", args.t_equi)
print("Relaxation temperature [K]:", args.t_relax)
print("Production temperature [K]:", args.t_prod)
print("Equilibration steps:", args.steps_equi)
print("Relaxation steps:", args.steps_relax)
print("Production steps:", args.steps_prod)
print("Density functional:", args.func)
print("Pseudopotential:", pp_func)
print("Basis set:", args.basis)
print("Calculate Wannier functions:", args.wannier)
print("")

# create a dictionary with the arguments and add pp_func
args_dict = vars(args)
args_dict["pp_func"] = pp_func

#############################################

# get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# check if all relevant files are present in the script directory
# if not, print warning and exit
files = [script_dir + "/input/geoopt.inp", script_dir + "/input/eq.inp",
         script_dir + "/input/relax.inp", script_dir + "/input/prod.inp", script_dir + "/data/BASIS_MOLOPT", script_dir + "/data/GTH_POTENTIALS", script_dir + "/data/dftd3.dat", script_dir + "/execute/run_cp2k_hedy.sh"]
for f in files:
    if not os.path.isfile(f):
        sys.exit(" *** Warning: Input file '" + f +
                 "' does not exist. Reinstall this setup tool. Exiting.")

# get the absolute path of the project directory
project_dir = os.path.abspath(args.project)

# get the abs path of the directory from which the script is called
start_dir = os.getcwd()

# get absolute path of the coordinate file
abs_coord = os.path.abspath(args.coord)
# get basename of the coordinate file
coord_basename = os.path.basename(abs_coord)

# change to the project directory
os.chdir(project_dir)

# check if the coordinate file exists
# if yes, copy it to the project directory
if os.path.isfile(abs_coord):
    os.system("cp " + abs_coord + " .")
# print warning if not
else:
    print(" *** Warning: coordinate file '" + abs_coord + "' does not exist.")
    print("     This will cause an error in CP2K if you do not add it afterwards.\n")

# copy the template files to the project directory
os.system("cp " + script_dir + "/input/* .")

# get a list of the input files and check it
cp2k_infiles = getFileList(".", "*.inp")
if len(cp2k_infiles) != 4:
    sys.exit(
        " *** Error: There should be 4 CP2K input files in the project directory.")

# reorder the list of input files: geometry, equilibration, relaxation, production
cp2k_infiles = [cp2k_infiles[1], cp2k_infiles[0],
                cp2k_infiles[3], cp2k_infiles[2]]

# adjust the input files
routines.adjust_cp2k_input(cp2k_infiles, args_dict)

# copy run script to project directory
os.system("cp " + script_dir + "/execute/run_cp2k_hedy.sh .")

# adjust the job name in the run script
routines.adjust_runscript("run_cp2k_hedy.sh", args.project)

# copy the cp2k data files to the project directory
os.system("cp " + script_dir + "/data/* .")

# in the end, change back to the directory from which the script was called
os.chdir(start_dir)

# print a message that the script has finished
print("Finished setting up the project '" + str(args.project) + "'.")
