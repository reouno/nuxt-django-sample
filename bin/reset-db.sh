#!/bin/sh
set -eux

# move to the directory
cd "$(dirname $0)"

# delete db
rm -f ../backend/backend/db.sqlite3

# migration
cd ../backend && python manage.py migrate

# create seed data
python manage.py loaddata backend/apps/accounts/fixtures/gender-master.json
python manage.py loaddata backend/apps/accounts/fixtures/users.json
