#!/bin/bash

set -e

build_type="${!:-debug}"

if [ "$build_type" = "debug" ]; then
  echo "DEBUG"
  cmake --build cmake-build-debug --target rocksdb-benchmark-harness -- -j"$(nproc)" && ./cmake-build-debug/rocksdb-benchmark-harness
elif [ "$build_type" = "release" ]; then
  echo "RELEASE"
  cmake --build cmake-build-release --target rocksdb-benchmark-harness -- -j"$(nproc)" && ./cmake-build-release/rocksdb-benchmark-harness
else
  echo "./run.sh debug|release"

fi
