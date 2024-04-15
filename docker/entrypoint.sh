#!/bin/bash

set -e

case $1 in
    load-fixtures)
        echo "→ Run load fixtures"
        sleep 3
        exec bash -c 'python fixtures/load_master_data.py && python fixtures/load_monitor_data.py'
        ;;

    run-migrations)
        echo "→ Run migrations"
        exec bash -c 'alembic upgrade head'
        ;;

    run-devel)
        /entrypoint.sh run-migrations
        LOADFIXTURES="${LOADFIXTURES:-false}"
        if [ "${LOADFIXTURES}" == "True" ]; then
            /entrypoint.sh load-fixtures
        fi
        echo "→ Running as development mode"
        DEBUGPY="${DEBUGPY:-false}"
        exec bash -c 'if [ "${DEBUGPY}" == "True" ]; then python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.asgi:app --host 0.0.0.0 --port 80 --reload --reload-dir /app --log-config logging.dev.yaml; else python -m uvicorn app.asgi:app --host 0.0.0.0 --port 80 --reload --reload-dir /app --log-config logging.dev.yaml; fi'
        ;;

    run-asgi)
        echo "→ Running as prod mode"
        exec uvicorn app.asgi:app --host 0.0.0.0 --port 80 --workers 5 --log-config logging.dev.yaml
        ;;

    *)
        exec "$@"
        ;;
esac
