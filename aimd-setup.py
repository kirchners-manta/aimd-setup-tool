#!/usr/bin/python3

# Script to setup an AIMD simualtion with CP2K
# written by Tom Frömbgen 2023-01-12

#############################################

# import modules
import sys
import argparse
import os
from pathlib import Path

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
                                 epilog="Written for the Kirchner group by Tom Frömbgen. Last modified 2023-01-12.",
                                 add_help=True)

parser.add_argument("-p", "--project", type=str,
                    help="project name", default="myproject")
parser.add_argument("-b", "--boxsize", type=float,
                    help="box size in Angstrom", default=20.0)
parser.add_argument("-c", "--coord", type=str,
                    help="coordinate file", default="simbox.xyz")
parser.add_argument("-t", "--thermo", type=str,
                    help="thermostat", default="nose")
parser.add_argument("--t-equi", type=float,
                    help="equilibration temperature in K", default=400.0)
parser.add_argument("--t-relax", type=float,
                    help="relaxation temperature in K", default=350.0)
parser.add_argument("--t-prod", type=float,
                    help="production temperature in K", default=350.0)
parser.add_argument("--steps-equi", type=int,
                    help="number of equilibration steps", default=20000)
parser.add_argument("--steps-relax", type=int,
                    help="number of relaxation steps", default=10000)
parser.add_argument("--steps-prod", type=int,
                    help="number of production steps", default=60000)

# parse arguments
args = parser.parse_args()

# print help if no arguments are given
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit()

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
print("")

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

# check if the coordinate file exists
if not os.path.isfile(args.coord):
    print(" *** Warning: coordinate file '" + args.coord + "' does not exist.")
    print("     This will cause an error in CP2K if you do not add it afterwards.\n")

# check if a valid thermostat was given. If no, print warning.
if args.thermo != "nose" and args.thermo != "csvr":
    print(" *** Warning: thermostat '" + args.thermo + "' is not valid.")
    print("     Valid options are 'nose' (Nose-Hoover) and 'csvr'.\n")
# else, capitalize the thermostat name
else:
    args.thermo = args.thermo.upper()

#############################################

# get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# get the absolute path of the project directory
project_dir = os.path.abspath(args.project)

# get the abs path of the directory from which the script is called
start_dir = os.getcwd()

# change to the project directory
os.chdir(project_dir)

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

# loop over the cp2k input files and adjust them according to user input
for i, file in enumerate(cp2k_infiles):

    # open the file
    with open(file, "r") as f:
        # the file is read into a list of lines, the string is changed and the file is written again
        lines = []
        lines = f.readlines()

        # for the geometry optimization: adjust project name, box length, coord file
        if i == 0:
            lines = [line.replace(
                "PROJECT_NAME project_name", "PROJECT_NAME " + str(args.project)) for line in lines]
            lines = [line.replace(
                "BOX_LENGTH box_length", "BOX_LENGTH " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "SIMBOX_XYZ simbox_xyz", "SIMBOX_XYZ " + str(args.coord)) for line in lines]
            with open(file, "w") as g:
                g.writelines(lines)

        # for the equilibration: adjust project name, box length, coord file, thermostat, temperature and number of steps
        elif i == 1:
            lines = [line.replace(
                "PROJECT_NAME project_name", "PROJECT_NAME " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "BOX_LENGTH box_length", "BOX_LENGTH " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "SIMBOX_XYZ simbox_xyz", "SIMBOX_XYZ " + str(args.coord)) for line in lines]
            lines = [line.replace("THERMO thermostat_type",
                                  "THERMO " + str(args.thermo)) for line in lines]
            lines = [line.replace(
                "TEMP temperature", "TEMP " + str(args.t_equi)) for line in lines]
            lines = [line.replace(
                "NSTEPS number_of_steps", "NSTEPS " + str(args.steps_equi)) for line in lines]
            with open(file, "w") as g:
                g.writelines(lines)

        # for the relaxation: adjust project name, box length, coord file, thermostat, temperature and number of steps
        elif i == 2:
            lines = [line.replace(
                "PROJECT_NAME project_name", "PROJECT_NAME " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "BOX_LENGTH box_length", "BOX_LENGTH " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "SIMBOX_XYZ simbox_xyz", "SIMBOX_XYZ " + str(args.coord)) for line in lines]
            lines = [line.replace("THERMO thermostat_type",
                                  "THERMO " + str(args.thermo)) for line in lines]
            lines = [line.replace(
                "TEMP temperature", "TEMP " + str(args.t_relax)) for line in lines]
            lines = [line.replace(
                "NSTEPS number_of_steps", "NSTEPS " + str(args.steps_relax)) for line in lines]
            with open(file, "w") as g:
                g.writelines(lines)

        # for the production: adjust project name, box length, coord file, thermostat, temperature and number of steps
        elif i == 3:
            lines = [line.replace(
                "PROJECT_NAME project_name", "PROJECT_NAME " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "BOX_LENGTH box_length", "BOX_LENGTH " + str(args.boxsize)) for line in lines]
            lines = [line.replace(
                "SIMBOX_XYZ simbox_xyz", "SIMBOX_XYZ " + str(args.coord)) for line in lines]
            lines = [line.replace("THERMO thermostat_type",
                                  "THERMO " + str(args.thermo)) for line in lines]
            lines = [line.replace(
                "TEMP temperature", "TEMP " + str(args.t_prod)) for line in lines]
            lines = [line.replace(
                "NSTEPS number_of_steps", "NSTEPS " + str(args.steps_prod)) for line in lines]
            with open(file, "w") as g:
                g.writelines(lines)

# copy run script to project directory
os.system("cp " + script_dir + "/execute/run_cp2k_hedy.sh .")

# adjust the job name in the run script
with open("./run_cp2k_hedy.sh", "r") as f:
    lines = []
    lines = f.readlines()
    lines = [line.replace("PROJECT_NAME", str(args.project)) for line in lines]
    with open("./run_cp2k_hedy.sh", "w") as g:
        g.writelines(lines)

# copy the cp2k data files to the project directory
os.system("cp " + script_dir + "/data/* .")

# in the end, change back to the directory from which the script was called
os.chdir(start_dir)

# print a message that the script has finished
print("Finished setting up the project '" + str(args.project) + "'.")
