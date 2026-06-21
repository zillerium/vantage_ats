#!/bin/bash
# 1. Clear out any old dump file if it exists
> all_code.txt

# 2. Grab main.py, then append all python files from your specific directories
cat main.py >> all_code.txt
cat services/*.py pipelines/*.py >> all_code.txt 2>/dev/null

echo "Done! All your custom code is now inside: all_code.txt"
