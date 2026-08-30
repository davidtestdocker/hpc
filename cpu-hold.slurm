#!/bin/bash

# Job name.
#SBATCH --job-name=cpu-hold

# Use the debug partition.
#SBATCH --partition=debug

# Request one node.
#SBATCH --nodes=1

# Request all 4 CPU tasks on this node.
#SBATCH --ntasks=4

# Save output using the Slurm job ID.
#SBATCH --output=cpu-hold-%j.out


# Show basic job information.
echo "JOB_ID=$SLURM_JOB_ID"
echo "NTASKS=$SLURM_NTASKS"
echo "NODE=$(hostname)"

# Launch 4 tasks.
# Each task sleeps for 60 seconds to keep resources occupied.
srun sleep 60
