#!/bin/sh
set -eux

# move to the directory
cd $(dirname $0)

# migration
cd ../backend && python manage.py migrate

# create seed data
python manage.py loaddata backend/apps/accounts/fixtures/users.json
python manage.py loaddata backend/apps/courses/fixtures/fixtures.json
