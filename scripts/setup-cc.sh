#!/bin/bash

set -e

echo "Installing system dependencies"
sudo apt-get update -y && sudo apt-get upgrade
sudo apt-get install git curl build-essential cmake sysstat libgflags-dev -y

echo "Installing rust"
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"
rustup default nightly

echo "Installing uv (for python)"
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "Setting up python"
cd vis
uv sync
cd ..

echo "Setting up cmake"
./reload-cmake.sh
