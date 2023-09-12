#!/usr/bin/env bash
set -e

envfile="${BK_HOME}/etc/bk_apigateway/bk_apigateway.env"
if [ -f "${envfile}" ]; then
    set -a
    source "${envfile}"
    set +a
fi

python manage.py collectstatic --no-input

command="gunicorn wsgi --env prometheus_multiproc_dir=/tmp/ -k gevent -w 4 -b [::]:${PORT:-6000} --max-requests ${GUNICORN_MAX_REQUESTS:-1000} --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-0} --timeout ${GUNICORN_TIMEOUT:-60} --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT:-30} --access-logfile - --error-logfile - --access-logformat '[%(h)s] %({request_id}i)s %(u)s %(t)s \"%(r)s\" %(s)s %(D)s %(b)s \"%(f)s\" \"%(a)s\"'"
exec bash -c "$command"