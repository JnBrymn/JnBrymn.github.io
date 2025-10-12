#!/usr/bin/env python3
"""
Script to fix inline math delimiters in Markdown files.

This script converts $$ inline math delimiters to $ while preserving display math.
The key challenge is distinguishing between inline and display math.

Rules:
1. Display math: $$ on its own line (or with only whitespace) should remain $$
2. Inline math: $$ within a line of text should become $
3. Handle edge cases like multiple math expressions on the same line
"""

import re
import sys
import os
from pathlib import Path


def fix_inline_math(content):
    """
    Fix inline math delimiters while preserving display math.
    
    Args:
        content (str): The markdown content to process
        
    Returns:
        tuple: (processed_content, number_of_changes)
    """
    lines = content.split('\n')
    result_lines = []
    change_count = 0
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            result_lines.append(line)
            continue
            
        # Check if this line contains only display math ($$ at start/end with optional whitespace)
        display_math_pattern = r'^\s*\$\$.*\$\$\s*$'
        if re.match(display_math_pattern, line):
            # This is display math, keep it as is
            result_lines.append(line)
            continue
            
        # For all other lines, convert $$ to $ for inline math
        # Use a more sophisticated approach to handle multiple math expressions per line
        
        # Split the line and process each part
        # Look for $$ patterns that are not display math
        processed_line = line
        
        # Find all $$ patterns and determine if they should be inline or display
        dollar_pattern = r'\$\$'
        matches = list(re.finditer(dollar_pattern, processed_line))
        
        # Process pairs of $$ delimiters
        i = 0
        while i < len(matches) - 1:
            start_match = matches[i]
            end_match = matches[i + 1]
            
            # Check if this is inline math (not at start/end of line with only whitespace)
            line_start = processed_line[:start_match.start()].strip()
            line_end = processed_line[end_match.end():].strip()
            
            # If there's text before the first $$ or after the second $$, it's inline math
            if line_start or line_end:
                # This is inline math, convert $$ to $
                old_line = processed_line
                processed_line = (processed_line[:start_match.start()] + 
                                processed_line[start_match.start():start_match.end()].replace('$$', '$') +
                                processed_line[start_match.end():end_match.start()] +
                                processed_line[end_match.start():end_match.end()].replace('$$', '$') +
                                processed_line[end_match.end():])
                
                # Count the changes (2 $$ -> $ conversions per math expression)
                if old_line != processed_line:
                    change_count += 2
                
                # Remove the processed matches from our list and continue
                matches = list(re.finditer(dollar_pattern, processed_line))
                i = 0  # Start over since we modified the string
            else:
                # This appears to be display math, skip it
                i += 2
                
        result_lines.append(processed_line)
    
    return '\n'.join(result_lines), change_count


def process_file(file_path):
    """
    Process a single markdown file.
    
    Args:
        file_path (Path): Path to the markdown file
        
    Returns:
        int: Number of changes made
    """
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Make a backup
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created backup: {backup_path}")
        
        # Process the content
        new_content, change_count = fix_inline_math(content)
        
        # Check if there were any changes
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  Updated {change_count} inline math delimiters")
            return change_count
        else:
            print(f"  No changes needed")
            return 0
            
    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return 0


def main():
    """Main function to process files."""
    if len(sys.argv) > 1:
        # Process specific files provided as arguments
        files_to_process = []
        for arg in sys.argv[1:]:
            file_path = Path(arg)
            if file_path.exists():
                files_to_process.append(file_path)
            else:
                print(f"File not found: {arg}")
        
        if not files_to_process:
            print("No valid files to process")
            return
            
    else:
        # Process all markdown files in the docs directory
        docs_dir = Path("docs")
        if not docs_dir.exists():
            print("docs directory not found")
            return
            
        files_to_process = list(docs_dir.rglob("*.md"))
        print(f"Found {len(files_to_process)} markdown files in docs directory")
    
    print(f"Processing {len(files_to_process)} files...")
    
    total_changes = 0
    files_with_changes = 0
    
    for file_path in files_to_process:
        changes = process_file(file_path)
        total_changes += changes
        if changes > 0:
            files_with_changes += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Files processed: {len(files_to_process)}")
    print(f"Files with changes: {files_with_changes}")
    print(f"Total changes made: {total_changes}")
    print(f"\nDone! Check the results and remove .backup files if everything looks good.")
    print("To remove backup files: find docs -name '*.backup' -delete")


if __name__ == "__main__":
    # python -m fix_inline_math
    main()
