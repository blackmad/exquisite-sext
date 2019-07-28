#!/bin/sh
REDIS_URL=redis://localhost:6379  gunicorn --worker-class eventlet -w 1 --timeout 300 chat:app -b 0.0.0.0:8000

