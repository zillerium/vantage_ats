#!/bin/bash

OUTPUT_FILE="combined_code.txt"

# Clear the output file if it already exists
> "$OUTPUT_FILE"

echo "Concatenating .py files into $OUTPUT_FILE..."

# Find files and loop through them safely
find . -type f -name "*.py" ! -path "*/venv/*" | while read -r file; do
    # 1. Add a visual header banner for clarity
    echo "==================================================" >> "$OUTPUT_FILE"
    echo "FILE: $file" >> "$OUTPUT_FILE"
    echo "==================================================" >> "$OUTPUT_FILE"
    
    # 2. Append the actual file contents
    cat "$file" >> "$OUTPUT_FILE"
    
    # 3. Add a couple of trailing newlines to separate files cleanly
    echo -e "\n\n" >> "$OUTPUT_FILE"
done

echo "Done! All code merged into $OUTPUT_FILE."
