#!/bin/bash

# Monitor script using POLLING (fallback for when inotifywait doesn't work)
# Checks file every 5 seconds for changes

FILE="/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK_FILE="/home/endrem/prosjekt/nanocode/agent_feedback.md"
MONITOR_LOG="/home/endrem/prosjekt/nanocode/monitor_log.txt"

POLL_INTERVAL=2  # Check every 2 seconds

# Function to log
log_monitor() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" >> "$MONITOR_LOG"
}

# Function to review code
review_code() {
    echo "" >> "$FEEDBACK_FILE"
    echo "## Review at $(date)" >> "$FEEDBACK_FILE"
    log_monitor "## Review started"
    
    echo "" >> "$FEEDBACK_FILE"
    echo "### Current code:" >> "$FEEDBACK_FILE"
    echo '```python' >> "$FEEDBACK_FILE"
    cat "$FILE" >> "$FEEDBACK_FILE"
    echo '```' >> "$FEEDBACK_FILE"
    echo "" >> "$FEEDBACK_FILE"
    
    echo "### Analysis:" >> "$FEEDBACK_FILE"
    
    # Syntax check
    if python3 -m py_compile "$FILE" 2>/dev/null; then
        echo "✅ **Syntax:** Valid" >> "$FEEDBACK_FILE"
        log_monitor "  ✅ Syntax valid"
    else
        echo "❌ **Syntax:** ERROR" >> "$FEEDBACK_FILE"
        log_monitor "  ❌ Syntax error"
    fi
    
    # Add fixes needed
    if ! grep -q "try:" "$FILE"; then
        echo "🔧 **Fix needed:** Wrap main() in try/except" >> "$FEEDBACK_FILE"
        log_monitor "  🔧 Need: try/except"
    fi
    
    if ! grep -q "input" "$FILE"; then
        echo "🔧 **Fix needed:** Add user input handling" >> "$FEEDBACK_FILE"
        log_monitor "  🔧 Need: input handling"
    fi
    
    echo "" >> "$FEEDBACK_FILE"
    echo "---" >> "$FEEDBACK_FILE"
    echo "" >> "$FEEDBACK_FILE"
    
    log_monitor "Review completed"
    echo "Review written"
}

# Function to add random feature
add_random_feature() {
    python3 << 'PYEOF'
import random
import datetime
import os

FILE = "/home/endrem/prosjekt/nanocode/hello_world.py"
FEEDBACK = "/home/endrem/prosjekt/nanocode/agent_feedback.md"
MONITOR_LOG = "/home/endrem/prosjekt/nanocode/monitor_log.txt"

creative_features = [
    ("import", "import time"),
    ("import", "import random"),
    ("import", "import sys"),
    ("function", "def get_greeting(): return random.choice(['Hello', 'Hi', 'Hey'])"),
    ("function", "def get_time(): return datetime.datetime.now().strftime('%H:%M:%S')"),
    ("in_main", "print(f'Random: {random.randint(1, 100)}')"),
    ("in_main", "print(f'Greeting: {get_greeting()}')" if "def get_greeting" in open(FILE).read() else "print('Nice to meet you!')"),
    ("comment", f"# Generated at {datetime.datetime.now().strftime('%H:%M:%S')}"),
]

with open(FILE, 'r') as f:
    content = f.read()
    lines = content.split('\n')

available = [f for f in creative_features if f[1] not in content]

if not available:
    with open(FEEDBACK, 'a') as f:
        f.write("🤖 **AUTO-UPDATE**: No new features available\n\n")
    with open(MONITOR_LOG, 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - All features present\n")
    print("All features present")
    exit(0)

typefeat, feat = random.choice(available)

# Apply feature
if typefeat == "import":
    lines.insert(1, feat)
elif typefeat == "function":
    for i, line in enumerate(lines):
        if "def main" in line:
            lines.insert(i, feat)
            lines.insert(i, "")
            break
elif typefeat == "in_main":
    for i, line in enumerate(lines):
        if "print" in line and "def main" not in line:
            lines.insert(i+1, f"    {feat}")
            break
elif typefeat == "comment":
    lines.insert(2, feat)

new_content = '\n'.join(lines)
with open(FILE, 'w') as f:
    f.write(new_content)

with open(FEEDBACK, 'a') as f:
    f.write(f"🤖 **AUTO-UPDATE**: [{typefeat}] {feat}\n\n")

with open(MONITOR_LOG, 'a') as f:
    f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ADDED: [{typefeat}] {feat}\n")

print(f"Added: [{typefeat}] {feat}")
PYEOF
}

# Main polling loop
echo "Polling Monitor Started"
echo "Checking every $POLL_INTERVAL seconds..."
log_monitor "=== POLLING MONITOR STARTED ==="

# Initial review
echo "Initial review..."
review_code

LAST_HASH=""

while true; do
    # Check if file exists
    if [ -f "$FILE" ]; then
        # Get current hash
        CURRENT_HASH=$(md5sum "$FILE" 2>/dev/null | cut -d' ' -f1)
        
        if [ "$CURRENT_HASH" != "$LAST_HASH" ] && [ -n "$LAST_HASH" ]; then
            echo ""
            echo "=== CHANGE DETECTED ==="
            log_monitor "=== CHANGE DETECTED ==="
            
            # Review
            review_code
            
            # Add feature
            echo "Adding creative feature..."
            log_monitor "Adding feature"
            add_random_feature
            
            # Re-review
            echo "Re-reviewing..."
            log_monitor "Re-review"
            review_code
            
            echo "Cycle complete. Waiting for next change..."
        fi
        
        LAST_HASH=$CURRENT_HASH
    fi
    
    sleep $POLL_INTERVAL
done
