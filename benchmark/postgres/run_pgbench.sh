#!/bin/bash

set -e

HOST="postgres-service"
USER="hpc"
DB="pgbench"

CLIENTS=${1:-10}
THREADS=${2:-2}
TRANSACTIONS=${3:-100}

RESULT_DIR="./results"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

RESULT_FILE="${RESULT_DIR}/pgbench_${TIMESTAMP}.log"


mkdir -p ${RESULT_DIR}


echo "================================"
echo " PostgreSQL Benchmark"
echo "================================"

echo "Host: ${HOST}"
echo "Database: ${DB}"
echo "Clients: ${CLIENTS}"
echo "Threads: ${THREADS}"
echo "Transactions/client: ${TRANSACTIONS}"

echo ""


pgbench \
  -h ${HOST} \
  -U ${USER} \
  -d ${DB} \
  -c ${CLIENTS} \
  -j ${THREADS} \
  -t ${TRANSACTIONS} \
  | tee ${RESULT_FILE}



