#!/bin/bash

echo "===== START  ====="
echo "START TIME: $(date)"

LOG_FILE="/app/logs/$(date +%Y%m%d).log"

/opt/venv/bin/python /app/mining_run.py --exec_set_id "$1"  > "$LOG_FILE" 2>&1

echo "END TIME: $(date)"
echo "=====  END  ====="
