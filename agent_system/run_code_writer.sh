#!/bin/bash
# Run code_writer and see what happens

echo "Starting code_writer.sh..."
echo "It will:"
echo "1. Read current code"
echo "2. Wait for reviews"
echo "3. Apply fixes"
echo "4. Clear feedback"
echo ""
echo "Current agent_feedback.md:"
cat /home/endrem/prosjekt/nanocode/agent_feedback.md
echo ""
echo "---"
echo ""
echo "Running code_writer.sh:"
echo ""

bash /home/endrem/prosjekt/nanocode/code_writer.sh
