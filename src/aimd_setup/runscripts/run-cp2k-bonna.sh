#!/bin/bash
#SBATCH --partition=long
#SBATCH --account=ag_mctc_kirchner
#SBATCH --ntasks=256 
#SBATCH --time=7-00:00:00
#SBATCH --nodes=8
#SBATCH --job-name=cp2k_2024.3
#SBATCH --output=cp2k.out 

export OMP_NUM_THREADS=1

module load OpenMPI/4.1.6-GCC-13.2.0
source /home/chemie/install_cp2k/cp2k-2024.3/tools/toolchain/install/setup
mpirun /home/chemie/install_cp2k/cp2k-2024.3/exe/local/cp2k.psmp  eq.inp > eq_output 
mpirun /home/chemie/install_cp2k/cp2k-2024.3/exe/local/cp2k.psmp  relax.inp > relax_output 
mpirun /home/chemie/install_cp2k/cp2k-2024.3/exe/local/cp2k.psmp  prod.inp > prod_output 
