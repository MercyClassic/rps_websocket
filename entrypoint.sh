#!/bin/bash
cd /game
alembic upgrade head
cd /game/src
gunicorn app.main.main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
