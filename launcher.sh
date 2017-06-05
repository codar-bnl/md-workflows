#!/bin/bash
module load boost
module load fftw
module load cudatoolkit
module use --append /lustre/atlas/world-shared/bip103/modules
module load openmpi/STATIC
module load gcc
export PATH=/ccs/proj/super/TOOLS/tau/tau-2.26.1/x86_64/bin/:$PATH
module use /lustre/atlas/world-shared/csc230/openmpi/modules/
module load openmpi/2017_03_24_6da4dbb-unsorted
export TAU_TRACE=1
tau_exec -T openmpi /lustre/atlas/world-shared/csc230/gromacs/bin/gmx_mpi mdrun -ntomp 1 -nb cpu -s topol.tpr -c out.gro
tau_treemerge.pl
tau_convert  -dumpname tau.trc tau.edf >> trace.txt
#tau_exec -T openmpi -ebs /lustre/atlas/scratch/aleang9/csc108/gromacs/bin/gmx_mpi mdrun -ntomp 1 -nb cpu -s topol.tpr -c out.gro
