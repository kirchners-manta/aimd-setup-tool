#!/bin/bash

# Part of the AIMD setup tool
# CP2K 2023.1 run script

#SBATCH -t 14-00:00:00
#SBATCH -p normal
#SBATCH --ntasks-per-node=N_CPU
#SBATCH --cpus-per-task=1
#SBATCH -N N_NODES
#SBATCH -J "PROJECT_NAME"

export OMP_NUM_THREADS=1
export OMP_PLACES=cores
export OMP_PROC_BIND=true

# load modules
module reset
module load VERSION_CP2K

# execute job
