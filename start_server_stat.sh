#!/bin/bash
PIDS=$(ps -ef | grep  'server_stat.py'|grep -v 'grep' | awk '{print $2}')

if [ -z "$PIDS" ]; then
  echo "No server_stat server to stop"
else
  kill -9 $PIDS
fi
sleep 3

python3 ./server_stat.py eslog 10.20.1.21  &