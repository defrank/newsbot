#!/bin/sh

cmd="python3 slackbot.py"
until $cmd; do
    echo "Slack bot crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
