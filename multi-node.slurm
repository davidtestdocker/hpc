#!/bin/bash

# Job name.
#SBATCH --job-name=multi-node-test

# Use the CPU partition.
#SBATCH --partition=cpu

# Request two compute nodes.
#SBATCH --nodes=2

# Run two tasks on each node.
#SBATCH --ntasks-per-node=2

#SBATCH --chdir=/tmp

# Save output using the job ID.
#SBATCH --output=multi-node-%j.out


# Show Slurm allocation information.
echo "JOB_ID=$SLURM_JOB_ID"
echo "NODELIST=$SLURM_JOB_NODELIST"
echo "NTASKS=$SLURM_NTASKS"

# Launch one hostname command per Slurm task.
srun hostname
