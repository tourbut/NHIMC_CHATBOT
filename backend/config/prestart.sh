#! /usr/bin/env bash


echo "Running Prestart"

# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head

echo "End Prestart"
