#!/bin/bash

# Part of the AIMD setup tool
# CP2K 2023.1 run script

#SBATCH -t 14-00:00:00
#SBATCH -p normal
#SBATCH --ntasks-per-node=N_CPU
#SBATCH --cpus-per-task=1
#SBATCH -N 1
#SBATCH -J "PROJECT_NAME"

export OMP_NUM_THREADS=1
export OMP_PLACES=cores
export OMP_PROC_BIND=true

# load modules
module reset
module load chem/CP2K/2023.1-foss-2022b-gcc-openmpi-openblas

# execute job

# BQB production
srun cp2k.psmp bqb.inp >bqb.out
