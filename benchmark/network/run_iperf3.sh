#!/bin/bash

set -e

SERVER=${1:-iperf3-server}
TIME=${2:-30}

echo "================================"
echo " Network Benchmark"
echo "================================"

echo "Server : ${SERVER}"
echo "Runtime: ${TIME}s"

echo ""

iperf3 \
    -c ${SERVER} \
    -t ${TIME}
