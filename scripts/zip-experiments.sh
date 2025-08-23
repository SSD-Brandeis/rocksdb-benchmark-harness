#!/bin/bash

set -e

tar --exclude=*.txt --exclude=*.ini --exclude=*.sh -czvf exp.tar.gz ./experiments
