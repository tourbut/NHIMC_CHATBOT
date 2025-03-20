#!/bin/bash

echo "===== START  ====="

LOG_FILE="/app/logs/$(date +%Y%m%d).log"

/opt/venv/bin/python /app/mining_run.py --exec_set_id "$1"  > "$LOG_FILE" 2>&1

echo "=====  END  ====="