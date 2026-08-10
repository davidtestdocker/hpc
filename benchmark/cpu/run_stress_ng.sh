#!/bin/bash

set -e

CPU_WORKERS=${1:-2}
TIMEOUT=${2:-60}

echo "================================"
echo " CPU Benchmark"
echo "================================"

echo "CPU Workers: ${CPU_WORKERS}"
echo "Duration: ${TIMEOUT}s"

echo ""

stress-ng \
  --cpu ${CPU_WORKERS} \
  --timeout ${TIMEOUT}s \
  --metrics-brief
