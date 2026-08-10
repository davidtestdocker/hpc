# CPU Benchmark Result

## Environment

Platform:
GKE Kubernetes

Node:
gke-hpc-dev-primary-pool-1489cf18-vxpk

CPU Capacity:
2 cores


## Tool

stress-ng


## Command

stress-ng --cpu 2 --timeout 60s --metrics-brief


## Result

CPU saturation achieved.

Node CPU:

Before:
422m (21%)

During:
2000m (103%)


## Observation

stress-ng successfully saturated the Kubernetes node CPU.

The benchmark confirms that:

- Pod CPU usage comes from Node VM CPU resources.
- Kubernetes schedules workload onto Node hardware.
- CPU limit does not create physical CPU resources.
