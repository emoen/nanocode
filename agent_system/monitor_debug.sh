#!/bin/bash

FILE="/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK_FILE="/home/endrem/prosjekt/nanocode/agent_feedback.md"
MONITOR_LOG="/home/endrem/prosjekt/nanocode/monitor_log.txt"

echo "=== MONITOR DEBUG START ==="
echo "File: $FILE"
echo "Feedback: $FEEDBACK_FILE"
echo "Log: $MONITOR_LOG"
echo ""

# Check inotifywait
echo "Checking for inotifywait..."
if command -v inotifywait &> /dev/null; then
    echo "✅ inotifywait found: $(which inotifywait)"
    inotifywait --version 2>&1 | head -1
else
    echo "❌ inotifywait NOT found - need to install inotify-tools"
    echo ""
    echo "Install with:"
    echo "  sudo apt-get install inotify-tools    # Debian/Ubuntu"
    echo "  sudo yum install inotify-tools        # RHEL/CentOS"
    echo "  brew install inotify-tools            # macOS"
    exit 1
fi

echo ""
echo "Checking files..."
ls -la "$FILE" 2>/dev/null && echo "✅ File exists" || echo "❌ File missing"
ls -la "$FEEDBACK_FILE" 2>/dev/null && echo "✅ Feedback exists" || echo "❌ Feedback missing"

echo ""
echo "Starting test monitor..."
echo "Press Ctrl+C to stop"

# Simple test
while true; do
    echo "Waiting for change to $FILE..."
    inotifywait -e modify "$FILE"
    echo "CHANGE DETECTED at $(date)"
    echo "New content:"
    cat "$FILE"
    echo "---"
done
