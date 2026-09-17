#!/bin/bash
#SBATCH --job-name=pending-cpu-test
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=256M
#SBATCH --time=00:10:00

hostname
sleep 300
