#!/bin/bash

FILE="/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK_FILE="/home/endrem/prosjekt/nanocode/agent_feedback.md"

echo "STARTED"

# Check inotifywait
if ! command -v inotifywait &> /dev/null; then
    echo "ERROR: inotifywait missing"
    exit 1
fi

echo "inotifywait OK"

# Initial review
echo "Doing initial review..."
# ... (add review logic)

echo "Now monitoring..."
while true; do
    inotifywait "$FILE"
    echo "Change detected!"
done
