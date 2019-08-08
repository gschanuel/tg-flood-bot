#!/bin/sh
while true; do
  python bot.py &
  PID=$!
  inotifywait -e modify bot.py
  kill $PID
done
