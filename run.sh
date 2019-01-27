#!/usr/bin/env bash
trap 'kill $(jobs -p)' EXIT

# source .venv/bin/activate

redis-server /usr/local/etc/redis.conf &
# jupyter notebook --no-browser --port=8880 --config=./jupyter_notebooks/jupyter_notebook_config.py &
celery -A djax worker --loglevel=info &
# python manage.py runserver
waitress-serve --port=8000 djax.wsgi:application
