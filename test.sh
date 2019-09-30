#!/bin/sh
while true; do
  python db_handler.py &
  PID=$!
#  cat bot.py | ncat air 5556
  rm -rf __pycache__
  inotifywait -e modify db_handler.py settings.py
  kill $PID
done
