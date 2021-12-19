#!/bin/sh
set -eux

# move to the directory
cd $(dirname $0)

# UNINSTALL python packages
cd ../backend && pip uninstall "$@" && pip freeze > requirements.txt
