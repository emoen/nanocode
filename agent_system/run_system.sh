#!/bin/bash
# Start both monitor and code_writer for the automated system

echo "Starting automated code review system..."

# Start monitor in background
echo "Starting monitor.sh in background..."
bash /home/endrem/prosjekt/nanocode/monitor.sh > /home/endrem/prosjekt/nanocode/monitor.out 2>&1 &
MONITOR_PID=$!
echo "Monitor started with PID: $MONITOR_PID"

# Wait a moment for monitor to initialize
sleep 2

# Start code_writer
echo "Starting code_writer.sh..."
bash /home/endrem/prosjekt/nanocode/code_writer.sh

# Cleanup on exit
kill $MONITOR_PID 2>/dev/null
echo "System stopped"
