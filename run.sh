#!/usr/bin/env bash
trap 'kill $(jobs -p)' EXIT

# source .venv/bin/activate

redis-server /usr/local/etc/redis.conf &
celery -A djax worker --loglevel=info &
waitress-serve --port=8000 djax.wsgi:application
