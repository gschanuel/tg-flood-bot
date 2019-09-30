#!/bin/sh
while true; do
  python bot.py &
  PID=$!
#  cat bot.py | ncat air 5556
  rm -rf __pycache__
  inotifywait -e modify bot.py settings.py db_handler.py
  kill $PID
done
