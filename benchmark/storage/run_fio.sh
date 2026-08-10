#!/bin/bash

set -e

SIZE=${1:-1G}
RUNTIME=${2:-60}

echo "================================"
echo " Storage Benchmark"
echo "================================"

echo "Test Size: ${SIZE}"
echo "Runtime: ${RUNTIME}s"

echo ""

fio \
  --name=storage-test \
  --filename=/tmp/fio-test-file \
  --size=${SIZE} \
  --rw=readwrite \
  --bs=4k \
  --direct=1 \
  --runtime=${RUNTIME} \
  --time_based \
  --group_reporting
