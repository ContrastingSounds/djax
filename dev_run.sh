#!/usr/bin/env bash
trap 'kill $(jobs -p)' EXIT

# source .venv/bin/activate

python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python manage.py shell
python manage.py collectstatic --no-input

redis-server /usr/local/etc/redis.conf &
celery -A djax worker --loglevel=info &
waitress-serve --port=8000 djax.wsgi:application
