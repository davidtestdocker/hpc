#!/bin/bash

set -euo pipefail

RESULT_DIR="results/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${RESULT_DIR}"

run_benchmark() {
    NAME=$1
    COMMAND=$2
    LOG_FILE=$3

    echo ""
    echo "======================================"
    echo "${NAME}"
    echo "======================================"

    if eval "${COMMAND}" 2>&1 | tee "${RESULT_DIR}/${LOG_FILE}"; then
        echo "[PASS] ${NAME}"
    else
        echo "[FAIL] ${NAME}"
        echo ""
        echo "Benchmark stopped because ${NAME} failed."
        exit 1
    fi
}

echo "======================================"
echo " HPC AI Benchmark Framework"
echo "======================================"

echo ""
echo "Result Directory:"
echo "${RESULT_DIR}"

run_benchmark \
    "CPU Benchmark" \
    "bash cpu/run_stress_ng.sh 2 30" \
    "cpu.log"

run_benchmark \
    "Storage Benchmark" \
    "bash storage/run_fio.sh 1G 30" \
    "storage.log"

run_benchmark \
    "PostgreSQL Benchmark" \
    "bash postgres/run_pgbench.sh 10 2 100" \
    "postgres.log"

run_benchmark \
    "Network Benchmark" \
    "bash network/run_iperf3.sh iperf3-server 30" \
    "network.log"

echo ""
echo "======================================"
echo " Benchmark Summary"
echo "======================================"

echo "CPU          PASS"
echo "Storage      PASS"
echo "PostgreSQL   PASS"
echo "Network      PASS"

echo ""
echo "Result Directory: ${RESULT_DIR}"
echo "All benchmarks completed successfully."
