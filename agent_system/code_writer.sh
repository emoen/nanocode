#!/bin/bash

# Code Writer Script - Now uses AI Agent for intelligent code writing
# Uses nanocode.py's agent to read feedback and write code

echo "🚀 Starting Agent-Based Code Writer"
echo "===================================="
echo ""
echo "This script now uses the AI agent to:"
echo "  1. Read feedback from monitor"
echo "  2. Analyze current code"
echo "  3. Make intelligent code changes"
echo ""
echo "Starting Python agent..."
echo ""

cd /home/endrem/prosjekt/nanocode
python3 code_writer_agent.py
