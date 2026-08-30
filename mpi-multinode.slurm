#!/bin/bash

#SBATCH --job-name=mpi-multinode
#SBATCH --partition=cpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --chdir=/tmp
#SBATCH --output=/tmp/mpi-multinode-%j.out

# Show Slurm allocation information.
echo "JOB_ID=$SLURM_JOB_ID"
echo "NODELIST=$SLURM_JOB_NODELIST"
echo "NTASKS=$SLURM_NTASKS"

# Launch 4 MPI ranks across two compute nodes.
mpirun \
  --allow-run-as-root \
  --host compute-01:2,compute-02:2 \
  -np 4 \
  /tmp/mpi_hello
