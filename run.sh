#!/bin/sh
while true; do
  python bot.py &
  PID=$!
  cat bot.py | ncat air 5556
  rm -rf __pycache__
  inotifywait -e modify bot.py
  kill $PID
done
