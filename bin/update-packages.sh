#!/bin/sh
set -eux

# move to the directory
cd $(dirname $0)

# install python packages required at this repo
cd ../backend && pip install -r requirements.txt

# install node packages required at this repo
cd ../front && yarn
