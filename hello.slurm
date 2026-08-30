#!/bin/bash

# Job name shown in Slurm queue.
#SBATCH --job-name=hello-slurm

# Use the debug partition.
#SBATCH --partition=debug

# Request one node.
#SBATCH --nodes=1

# Request two CPU tasks.
#SBATCH --ntasks=2

# Write standard output to this file.
#SBATCH --output=hello-%j.out


# Show which compute node runs this job.
echo "Running on node: $(hostname)"

# Show the Slurm job ID.
echo "SLURM_JOB_ID=$SLURM_JOB_ID"

# Show how many tasks Slurm allocated.
echo "SLURM_NTASKS=$SLURM_NTASKS"

# Launch one hostname command per Slurm task.
srun hostname
