#!/bin/bash

# Created by the AIMD setup tool
# CP2K run script

#SBATCH -t 21-00:00:00
#SBATCH -p normal
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1
#SBATCH -N 1
#SBATCH -J "reftraj_ir_02"

export OMP_NUM_THREADS=1
export OMP_PLACES=cores
export OMP_PROC_BIND=true

# load modules
module reset
module load chem/CP2K/2025.1-foss-2023b-gcc-openmpi-openblas

# execute job
srun cp2k.psmp reftraj.inp >reftraj.out
