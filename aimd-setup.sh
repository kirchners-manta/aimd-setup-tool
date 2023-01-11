#!/bin/bash

# Script to setup an AIMD simualtion with CP2K
# written by Tom Frömbgen 2023-01-11

# exit upon error
set -eo pipefail

# read input from user
PNAME="setup-test"
BLENGTH="12.34"
COORDS="simbox.xyz"

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
    echo -e "Project name: $PNAME"
    mkdir $PDIR
fi

# if no box dimensions are given, inform user. No exit
if [ -z $BLENGTH ]; then
    echo -e "\n *** WARNING: No box dimensions given. Will cause CP2K crash! ***\n"
else
    echo -e "Box length (Angstrom): $BLENGTH"
fi

# if no coordinates are given, inform user. No exit
if [ -z $COORDS ]; then
    echo -e "\n *** WARNING: No system coordintes given. Will cause CP2K crash! ***\n"
else
    echo -e "Coordinates of system taken from: $COORDS"
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
done

# copy the cluster run script and adjust it
cp $TEMPLATEDIR/execute/* .
sed -i "s@PROJECT_NAME@$PNAME@" run_cp2k_hedy.sh

# copy basis set, potential and dispersion files
cp $TEMPLATEDIR/cp2k/* .

# change back to directory from where this script was called
popd >/dev/null
echo "Setup successful"
