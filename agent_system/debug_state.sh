#!/bin/bash
echo "=== DEBUG STATE ==="
echo ""
echo "hello_world.py:"
cat /home/endrem/prosjekt/nanocode/hello_world.py
echo ""
echo "---"
echo ""
echo "agent_feedback.md size: $(wc -c < /home/endrem/prosjekt/nanocode/agent_feedback.md) bytes"
echo ""
cat /home/endrem/prosjekt/nanocode/agent_feedback.md
echo ""
echo "---"
echo ""
echo "monitor_log.txt (last 10 lines):"
tail -10 /home/endrem/prosjekt/nanocode/monitor_log.txt 2>/dev/null || echo "No monitor log"
echo ""
echo "=== END DEBUG ==="
