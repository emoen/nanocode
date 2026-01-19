#!/bin/bash
echo "=== Checking Monitor Status ==="
echo ""
echo "hello_world.py:"
tail -5 /home/endrem/prosjekt/nanocode/hello_world.py
echo ""
echo "monitor_log.txt (last 20 lines):"
tail -20 /home/endrem/prosjekt/nanocode/monitor_log.txt 2>/dev/null || echo "No log entries"
echo ""
echo "agent_feedback.md (last 30 lines):"
tail -30 /home/endrem/prosjekt/nanocode/agent_feedback.md
echo ""
echo "=== End Check ==="
