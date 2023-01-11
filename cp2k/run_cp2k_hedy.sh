#!/bin/bash
# PBS Job
#PBS -V
#PBS -N dmso-bulk
#PBS -m ae
#PBS -l nodes=1:ppn=64
#PBS -q hedy
#
# For iris and hedy (only one node)

# load software
source /home/brehm/Software_2021/load_environment_2021.sh
export CP2K_PATH=/home/brehm/Software_2021/bin/cp2k_8.1.psmp

# generate scratch directory
mkdir -p /tmp1/$USER
mkdir /tmp1/$USER/$PBS_JOBID

# copy files to scratch
cp -r $PBS_O_WORKDIR/* /tmp1/$USER/$PBS_JOBID
cd /tmp1/$USER/$PBS_JOBID

# generate hostfile
echo $(pwd) >hosts_file
export PARNODES=$(wc -l $PBS_NODEFILE | gawk '{print $1}')
cat $PBS_NODEFILE >hosts_file

# execute job
which mpirun
mpirun $CP2K_PATH geoopt.inp >geoopt.out
mpirun $CP2K_PATH eq.inp >eq.out
mpirun $CP2K_PATH relax.inp >relax.out
mpirun $CP2K_PATH prod.inp >prod.out

# copy files back and clean up
cd $PBS_O_WORKDIR
cp -r /tmp1/$USER/$PBS_JOBID/* $PBS_O_WORKDIR
rm -r /tmp1/$USER/$PBS_JOBID
