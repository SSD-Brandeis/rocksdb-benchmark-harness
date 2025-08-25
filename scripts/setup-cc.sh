#!/bin/bash
set -e

echo "Installing system dependencies"
sudo apt-get update -y
sudo apt-get install -y git curl build-essential cmake sysstat libgflags-dev openjdk-17-jdk maven

echo "Installing Rust"
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "$HOME/.cargo/env"
rustup default nightly

echo "Installing uv (Python dependency manager)"
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

echo "Setting up Python environment"
cd vis
uv sync
cd ..

echo "Updating git submodules"
git submodule update --init --recursive

echo "Building YCSB"
cd vendor/YCSB
mvn clean package -DskipTests
cd ../..

echo "Reloading CMake and building harness"
./reload-cmake.sh
cmake --build cmake-build-release --target rocksdb-benchmark-harness -- -j"$(nproc)"

echo "Setup complete"
