#!/bin/bash
# PBS Job
#PBS -V
#PBS -N PROJECT_NAME
#PBS -m ae
#PBS -l nodes=1:ppn=N_CPU
#PBS -q berta2
#

# create temporary directories
mkdir -p /tmp1/$USER
cd $PBS_O_WORKDIR

mkdir /tmp1/$USER/$PBS_JOBID
cp -r $PBS_O_WORKDIR/* /tmp1/$USER/$PBS_JOBID
cd /tmp1/$USER/$PBS_JOBID


# Load necessary modules
export PATH=/software/cluster-2/gcc-11.4.0/bin:/software/cluster-2/openmpi-4.1.6_gcc_11.4/bin:$PATH
export LD_LIBRARY_PATH=/software/cluster-2/gcc-11.4.0/lib64:/software/cluster-2/openmpi-4.1.6_gcc_11.4/lib64:$LD_LIBRARY_PATH
export OMPI_MCA_mpi_leave_pinned=0
export PARNODES=`wc -l $PBS_NODEFILE |gawk '{print $1}'`
export SDIR=$TMP/$PBS_JOBID
export HOMEDIR=$PBS_O_WORKDIR
which mpirun
source VERSION_CP2K/setup

# print compute node information
cat $PBS_NODEFILE>hosts_file
echo $SDIR >tmp_dir

# execute job


# clean up
cp -r /tmp1/$USER/$PBS_JOBID/* $PBS_O_WORKDIR
cd $PBS_O_WORKDIR
rm -r /tmp1/$USER/$PBS_JOBID
