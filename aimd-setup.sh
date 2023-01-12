#!/bin/bash

# Script to setup an AIMD simualtion with CP2K
# written by Tom Frömbgen 2023-01-11

# exit upon error
set -eo pipefail

# read input from user via command line using input flags
# -p: project name
# -b: box length
# -c: coordinates of system
# -t: thermostat
while getopts "p:b:c:t:" opt; do
    case $opt in
    p)
        PNAME=$OPTARG
        echo "Project name: $PNAME"
        ;;
    b)
        BLENGTH=$OPTARG
        echo "Box length (Angstrom): $BLENGTH"
        ;;
    c)
        COORDS=$OPTARG
        echo "Coordinates of system taken from: $COORDS"
        ;;
    t)
        THERMO=$OPTARG
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    ?)
        echo "Usage: aimd-setup -p project_name -b box_length -c coordinates -t thermostat (optional)"
        exit 1
        ;;
    esac
done

# shift the input flags so that the remaining arguments are the ones to be used
shift $((OPTIND - 1))

# default vals
THERMO_DEFAULT="NOSE"

# check input and inform user what happens
PDIR="$(pwd)/$PNAME"
TEMPLATEDIR="/home/froembgen/phd/aimd-template"
# if no project name is given, exit
if [ -z $PNAME ]; then
    echo -e "No project name given."
    exit 1
# if project directory already exists, exit
elif [ -d $(pwd)/$PNAME ]; then
    echo -e "Project directory already exists. Remove it or choose other project name."
    exit 1
# else, create directory
else
    echo -e "Setting up an AIMD simulation in $PDIR"
    mkdir $PDIR
fi

# if no box dimensions are given, inform user. No exit
if [ -z $BLENGTH ]; then
    echo -e "\n *** WARNING: No box dimensions given. Will cause CP2K crash! ***\n"
fi

# if no coordinates are given, inform user. No exit
if [ -z $COORDS ]; then
    echo -e "\n *** WARNING: No system coordintes given. Will cause CP2K crash! ***\n"
fi

# if no thermostat is given, take default value
# if thermostat is given, check if it is valid
# valid thermostats: NOSE or CSVR
if [ -z $THERMO ]; then
    echo -e "Thermostat (default): $THERMO_DEFAULT"
    THERMO=$THERMO_DEFAULT
elif [ $THERMO == "nose" ]; then
    echo -e "Thermostat: NOSE"
    THERMO="NOSE"
elif [ $THERMO == "csvr" ]; then
    echo -e "Thermostat: CSVR"
    THERMO="CSVR"
else
    echo -e "\n *** WARNING: Invalid thermostat. Will cause CP2K crash! ***\n"
fi

# change to the project directory and start setup
pushd $PDIR >/dev/null

# copy cp2k input files to the created directory
cp $TEMPLATEDIR/input/* .

# adjust CP2K input files according to user input
infiles=("eq.inp" "geoopt.inp" "prod.inp" "relax.inp")
for file in ${infiles[@]}; do
    sed -i "s@project_name@$PNAME@g" $file
    sed -i "s@box_length@$BLENGTH@g" $file
    sed -i "s@simbox_xyz@$COORDS@g" $file
    sed -i "s@thermostat_type@$THERMO@g" $file
done

# copy the cluster run script and adjust it
cp $TEMPLATEDIR/execute/* .
sed -i "s@PROJECT_NAME@$PNAME@" run_cp2k_hedy.sh

# copy basis set, potential and dispersion files
cp $TEMPLATEDIR/cp2k/* .

# change back to directory from where this script was called
popd >/dev/null
echo -e "\nSetup successful! \n"
