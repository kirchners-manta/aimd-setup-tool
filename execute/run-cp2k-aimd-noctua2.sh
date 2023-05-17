#!/bin/bash

# run script for CP2K 9.1 on Noctua2
# written by Tom Frömbgen 2023-05-01

#SBATCH -t 7-00:00:00
#SBATCH -p normal
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH -N 2
#SBATCH -J "PROJECT_NAME"

export OMP_NUM_THREADS=1
export OMP_PLACES=cores
export OMP_PROC_BIND=true

# load modules
module reset
module load chem/CP2K/9.1-foss-2021b

# execute job

# AIMD simulation
srun cp2k.psmp geoopt.inp >geoopt.out
srun cp2k.psmp eq.inp >eq.out
srun cp2k.psmp relax.inp >relax.out
srun cp2k.psmp prod.inp >prod.out
