#!/bin/bash
#SBATCH --partition=intelsr_long
#SBATCH --account=ag_mctc_kirchner
#SBATCH --ntasks=N_CPU
#SBATCH --time=7-00:00:00
#SBATCH --nodes=N_NODES
#SBATCH --job-name="PROJECT_NAME"

export OMP_NUM_THREADS=1

# load modules
module load OpenMPI/4.1.5-GCC-12.3.0

# setup file
source VERSION_CP2K/tools/toolchain/install/setup

# execute job
