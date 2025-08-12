#!/bin/bash

# Part of the AIMD setup tool
# CP2K 2024.3 run script

#SBATCH --partition=long
#SBATCH --account=ag_mctc_kirchner
#SBATCH --ntasks=N_CPU
#SBATCH --time=7-00:00:00
#SBATCH --nodes=N_NODES
#SBATCH --job-name="PROJECT_NAME"

export OMP_NUM_THREADS=1

#load modules
module load OpenMPI/4.1.6-GCC-13.2.0
source VERSION_CP2K/tools/toolchain/install/setup

# execute job
