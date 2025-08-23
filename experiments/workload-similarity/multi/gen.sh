#!/bin/bash

set -e

files=()
for f in *.spec.json; do
    files+=("$(realpath "$f")")
done

cd /home/ott/Documents/code/ssd/rocksdb-benchmark-harness/vendor/tectonic
RUST_LOG="info" cargo r --release -- generate \
  -w /home/ott/Documents/code/ssd/rocksdb-benchmark-harness/experiments/workload-similarity/multi/ \
  -o /home/ott/Documents/code/ssd/rocksdb-benchmark-harness/experiments/workload-similarity/multi/
cd -
#for f in "${files[@]}"; do
#  cargo r --release -- generate \
#    -w "$f" \
#    -o /home/ott/Documents/code/ssd/rocksdb-benchmark-harness/experiments/workload-similarity/multi/
#  echo "$f"
#done

#cd ..
#cd ..
