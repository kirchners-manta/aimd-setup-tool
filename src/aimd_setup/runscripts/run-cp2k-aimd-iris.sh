#!/bin/bash

# Part of the AIMD setup tool
# CP2K 2022.1 run script

# PBS Job
#PBS -N PROJECT_NAME
#PBS -l nodes=1:ppn=N_CPU
#PBS -q QUEUE_NAME

# For iris and hedy (only one node)

# load software
# load software
# openmpi 4.1.4
export PATH=/software/cluster-2/openmpi-4.1.4/bin:$PATH
export LD_LIBRARY_PATH=/software/cluster-2/openmpi-4.1.4/lib64:/usr/lib64/mpi/gcc/openmpi4/lib64/:$LD_LIBRARY_PATH

# cp2k 2022.1
source /software/cluster-2/cp2k-2022.1/setup
export CP2K_PATH=/software/cluster-2/cp2k-2022.1/cp2k.psmp

# generate scratch directory
mkdir -p /tmp1/$USER
mkdir /tmp1/$USER/$PBS_JOBID

# copy files to scratch
cp -r $PBS_O_WORKDIR/* /tmp1/$USER/$PBS_JOBID

# change to scratch and generate hostfile
cd /tmp1/$USER/$PBS_JOBID
echo $(pwd) >hosts_file
export PARNODES=$(wc -l $PBS_NODEFILE | gawk '{print $1}')
cat $PBS_NODEFILE >hosts_file

# execute job
which mpirun

# AIMD simulation
mpirun $CP2K_PATH geoopt.inp >geoopt.out
mpirun $CP2K_PATH eq.inp >eq.out
mpirun $CP2K_PATH relax.inp >relax.out
mpirun $CP2K_PATH prod.inp >prod.out

# copy files back and clean up
cd $PBS_O_WORKDIR
cp -r /tmp1/$USER/$PBS_JOBID/* $PBS_O_WORKDIR
rm -r /tmp1/$USER/$PBS_JOBID
