#!/bin/bash
# Test if monitor_polling.sh writes to agent_feedback.md

FILE="/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK="/home/endrem/prosjekt/nanocode/agent_feedback.md"
LOG="/home/endrem/prosjekt/nanocode/monitor_log.txt"

# Force a change
echo "# TEST CHANGE $(date)" >> "$FILE"

sleep 3

echo "=== Checking results ==="
echo "agent_feedback.md:"
cat "$FEEDBACK"
echo ""
echo "monitor_log.txt (last 5):"
tail -5 "$LOG"
