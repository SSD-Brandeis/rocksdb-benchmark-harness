#!/bin/bash

set -e

RUNS=5
EXPERIMENT_PATH=$(realpath "./experiments/workload-similarity/")

echo "Building tectonic"
cd vendor/tectonic
CARGO_TARGET_DIR="target" cargo build --release
cd ../..

echo "Building rocksdb-benchmark-harness"
cmake --build cmake-build-release --target rocksdb-benchmark-harness -- -j"$(nproc)"

function generate_tectonic_workload() {
  echo "generating tectonic workload"
  ./vendor/tectonic/target/release/tectonic-cli generate \
    -w "${EXPERIMENT_PATH}/workload-a.spec.json" \
    -o "${EXPERIMENT_PATH}/tec-workload-a.txt"
}

function generate_ycsb_workload() {
  echo "generating ycsb workload"
  cd vendor/YCSB
  /usr/lib/jvm/java-17-openjdk-amd64/bin/java \
    -cp /home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/YCSB/file/conf:/home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/YCSB/file/target/file-binding-0.18.0-SNAPSHOT.jar:/home/ott/.m2/repository/org/apache/htrace/htrace-core4/4.1.0-incubating/htrace-core4-4.1.0-incubating.jar:/home/ott/.m2/repository/org/hdrhistogram/HdrHistogram/2.1.12/HdrHistogram-2.1.12.jar:/home/ott/.m2/repository/org/codehaus/jackson/jackson-mapper-asl/1.9.4/jackson-mapper-asl-1.9.4.jar:/home/ott/.m2/repository/org/codehaus/jackson/jackson-core-asl/1.9.4/jackson-core-asl-1.9.4.jar:/home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/YCSB/core/target/core-0.18.0-SNAPSHOT.jar site.ycsb.Client \
    -db site.ycsb.db.FileClient \
    -P workloads/workloada \
    -p "file.output=${EXPERIMENT_PATH}/ycsb-workload.1.part" \
    -p recordcount=1000000 \
    -p operationcount=1000000 \
    -load

  /usr/lib/jvm/java-17-openjdk-amd64/bin/java \
    -cp /home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/YCSB/file/conf:/home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/YCSB/file/target/file-binding-0.18.0-SNAPSHOT.jar:/home/ott/.m2/repository/org/apache/htrace/htrace-core4/4.1.0-incubating/htrace-core4-4.1.0-incubating.jar:/home/ott/.m2/repository/org/hdrhistogram/HdrHistogram/2.1.12/HdrHistogram-2.1.12.jar:/home/ott/.m2/repository/org/codehaus/jackson/jackson-mapper-asl/1.9.4/jackson-mapper-asl-1.9.4.jar:/home/ott/.m2/repository/org/codehaus/jackson/jackson-core-asl/1.9.4/jackson-core-asl-1.9.4.jar:/home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/YCSB/core/target/core-0.18.0-SNAPSHOT.jar site.ycsb.Client \
    -db site.ycsb.db.FileClient \
    -P workloads/workloada \
    -p "file.output=${EXPERIMENT_PATH}/ycsb-workload.2.part" \
    -p recordcount=1000000 \
    -p operationcount=1000000 \
    -t

  cat "${EXPERIMENT_PATH}/ycsb-workload.1.part" "${EXPERIMENT_PATH}/ycsb-workload.2.part" >"${EXPERIMENT_PATH}/ycsb-workload-a.txt"
  rm "${EXPERIMENT_PATH}/ycsb-workload.1.part" "${EXPERIMENT_PATH}/ycsb-workload.2.part"
  cd ../..
}

 ./cmake-build-release/rocksdb-benchmark-harness \
   ./experiments/workload-similarity/rocksdb-options.ini \
   ./experiments/workload-similarity/tec-workload-a.txt >"${EXPERIMENT_PATH}/ops.json"

 for i in $(seq 1 "$RUNS"); do
   echo "tectonic iostat run $i"
   generate_tectonic_workload
   generate_ycsb_workload

   iostat -d 1 nvme0n1 -o JSON >"./experiments/workload-similarity/iostat.tectonic.$i.json" &
   IOSTAT_PID=$!
   sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

   ./cmake-build-release/rocksdb-benchmark-harness \
     ./experiments/workload-similarity/rocksdb-options.ini \
     ./experiments/workload-similarity/tec-workload-a.txt

   kill -INT $IOSTAT_PID

   echo "YCSB iostat run $i"
   iostat -d 1 nvme0n1 -o JSON >"./experiments/workload-similarity/iostat.ycsb.$i.json" &
   IOSTAT_PID=$!
   sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

   ./cmake-build-release/rocksdb-benchmark-harness \
     ./experiments/workload-similarity/rocksdb-options.ini \
     ./experiments/workload-similarity/ycsb-workload-a.txt

   kill -INT $IOSTAT_PID

 done
