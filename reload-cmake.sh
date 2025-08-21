#!/bin/bash

set -e

mkdir -p cmake-build-debug
cd cmake-build-debug
cmake .. -DCMAKE_BUILD_TYPE=Debug
cd ..

mkdir -p cmake-build-release
cd cmake-build-release
cmake .. -DCMAKE_BUILD_TYPE=Release
cd ..

mkdir -p cmake-build-release-with-stats
cd cmake-build-release-with-stats
cmake .. -DCMAKE_BUILD_TYPE=Release -DSTATS="on"
cd ..
