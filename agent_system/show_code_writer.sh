#!/bin/bash
echo "Search for main_loop:"
grep -n "main_loop" /home/endrem/prosjekt/nanocode/code_writer.sh
echo ""
echo "Around line 260:"
sed -n '258,270p' /home/endrem/prosjekt/nanocode/code_writer.sh
