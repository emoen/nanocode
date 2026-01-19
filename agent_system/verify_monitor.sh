#!/bin/bash
# Verify what monitor_polling.sh is doing

FILE="/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK="/home/endrem/prosjekt/nanocode/agent_feedback.md"

echo "=== Verify Monitor ==="
echo ""
echo "Does monitor_polling.sh have review_code function?"
grep -A 5 "review_code()" /home/endrem/prosjekt/nanocode/monitor_polling.sh | head -10

echo ""
echo "Does it write to FEEDBACK_FILE?"
grep "FEEDBACK_FILE" /home/endrem/prosjekt/nanocode/monitor_polling.sh

echo ""
echo "Current feedback file:"
cat "$FEEDBACK"

echo ""
echo "Making a test change to trigger monitor..."
echo "# TEST TRIGGER" >> "$FILE"
echo "Wait 3 seconds..."
sleep 3
echo "Feedback file now:"
cat "$FEEDBACK"
