#!/bin/bash

LOG_FILE="/app/logs/$(date +%Y%m%d).log"
python mining_run.py --exec_set_id "$1"  > "$LOG_FILE" 2>&1
