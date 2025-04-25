#!/usr/bin/env bash
# start.sh

gunicorn instafi_agents.wsgi --bind 0.0.0.0:$PORT --workers 4