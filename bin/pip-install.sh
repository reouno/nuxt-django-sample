#!/bin/sh
set -eux

# move to the directory
cd $(dirname $0)

# install new python packages and add them to the requirements
cd ../backend && pip install "$@" && pip freeze > requirements.txt
