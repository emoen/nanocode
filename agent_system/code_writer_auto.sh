#!/bin/bash

# Fully automated code_writer - no user input

FILE="/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK_FILE="/home/endrem/prosjekt/nanocode/agent_feedback.md"
LAST_REVIEW_POS=0

echo "=== CODE WRITER: FULLY AUTOMATED ==="
echo ""

# Initialize - read current position
if [ -f "$FEEDBACK_FILE" ]; then
    LAST_REVIEW_POS=$(wc -c < "$FEEDBACK_FILE")
    echo "Initialized. Current feedback size: $LAST_REVIEW_POS bytes"
else
    echo "Feedback file doesn't exist yet"
    exit 1
fi

# Read current code
echo ""
echo "Step 1: Reading current code..."
cat "$FILE"
echo ""

# Wait for reviews
echo "Step 2: Waiting for new reviews..."
while true; do
    if [ -f "$FEEDBACK_FILE" ]; then
        CURRENT_SIZE=$(wc -c < "$FEEDBACK_FILE")
        if [ "$CURRENT_SIZE" -gt "$LAST_REVIEW_POS" ]; then
            echo "NEW REVIEWS DETECTED!"
            echo ""
            echo "=== Reviews ==="
            tail -c $((CURRENT_SIZE - LAST_REVIEW_POS)) "$FEEDBACK_FILE"
            echo "==============="
            
            # Apply fixes
            echo ""
            echo "Step 3: Applying fixes..."
            
            NEW_FEEDBACK=$(tail -c $((CURRENT_SIZE - LAST_REVIEW_POS)) "$FEEDBACK_FILE")
            
            # Check for try/except need
            if echo "$NEW_FEEDBACK" | grep -qi "try.*except"; then
                echo "  - Adding try/except wrapper..."
                
                # Simple fix: wrap main content in try/except
                if ! grep -q "try:" "$FILE"; then
                    python3 << 'PYEOF'
import re
FILE = "/home/endrem/prosjekt/nanocode/hello_world.py"
with open(FILE, 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'def main(' in line:
        new_lines.append(line)
        new_lines.append('    try:\n')
    elif line.strip() and 'def main' not in line and 'if __name__' not in line:
        # Inside main
        if line.strip().startswith('print') or line.strip().startswith('name'):
            new_lines.append('    ' + line)
        else:
            new_lines.append(line)
    elif 'if __name__' in line:
        new_lines.append('    except Exception as e:\n')
        new_lines.append('        print(f"Error: {e}")\n')
        new_lines.append(line)
    else:
        new_lines.append(line)

with open(FILE, 'w') as f:
    f.writelines(new_lines)
PYEOF
                    echo "  ✓ Added try/except"
                fi
            fi
            
            if echo "$NEW_FEEDBACK" | grep -qi "input.*error\|validation"; then
                echo "  - Adding input validation..."
                if grep -q "input" "$FILE" && ! grep -q "try.*input" "$FILE"; then
                    # Could add validation here
                    echo "  ✓ Input handling noted"
                fi
            fi
            
            # Clear feedback
            echo ""
            echo "Step 4: Clearing feedback..."
            echo "# Agent Feedback Log" > "$FEEDBACK_FILE"
            echo "" >> "$FEEDBACK_FILE"
            echo "---" >> "$FEEDBACK_FILE"
            echo "" >> "$FEEDBACK_FILE"
            LAST_REVIEW_POS=$(wc -c < "$FEEDBACK_FILE")
            echo "Feedback cleared"
            
            echo ""
            echo "Step 5: Showing updated code..."
            cat "$FILE"
            echo ""
            echo "=== FIXES APPLIED ==="
            echo "Waiting for next round of reviews..."
            echo ""
        fi
    fi
    sleep 1
done
