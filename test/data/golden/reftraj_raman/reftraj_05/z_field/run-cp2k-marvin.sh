#!/bin/bash
#SBATCH --partition=intelsr_long
#SBATCH --account=ag_mctc_kirchner
#SBATCH --ntasks=96
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --job-name="reftraj_raman_05_z"

export OMP_NUM_THREADS=1

# load modules
module load OpenMPI/4.1.5-GCC-12.3.0

# setup file
source /opt/software/ag_mctc_kirchner/cp2k-2025.2/tools/toolchain/install/setup

# execute job
mpirun /opt/software/ag_mctc_kirchner/cp2k-2025.2/exe/local/cp2k.psmp reftraj.inp >reftraj.out
