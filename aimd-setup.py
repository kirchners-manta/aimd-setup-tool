#!/bin/python3

# Script to setup an AIMD simualtion with CP2K
# written by Tom Frömbgen 2023-01-12

#############################################

# import modules
import sys
import argparse
import os

# define command line arguments
parser = argparse.ArgumentParser(prog="aimd-setup.py",
                                 description="Script to setup an AIMD simualtion with CP2K",
                                 epilog="Written for the Kirchner group by Tom Frömbgen. Last modified 2023-01-12.",
                                 add_help=True)

parser.add_argument("-p","--project", type=str, help="project name", default="myproject")
parser.add_argument("-b", "--boxsize", type=float, help="box size in Angstrom", default=20.0)
parser.add_argument("-c", "--coord", type=str, help="coordinate file", default="simbox.xyz")
parser.add_argument("--thermo", type=str, help="thermostat", default="Nose-Hoover")
parser.add_argument("--t-equi", type=float, help="equilibration temperature in K", default=400.0)
parser.add_argument("--t-relax", type=float, help="relaxation temperature in K", default=350.0)
parser.add_argument("--t-prod", type=float, help="production temperature in K", default=350.0)
parser.add_argument("--steps-equi", type=int, help="number of equilibration steps", default=20000)
parser.add_argument("--steps-relax", type=int, help="number of relaxation steps", default=10000)
parser.add_argument("--steps-prod", type=int, help="number of production steps", default=60000)

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

# check if the coordinate file exists
if not os.path.isfile(args.coord):
    print("\n *** Warning: coordinate file", args.coord, "does not exist. This will cause an error in CP2K if you do not add it afterwards.\n")