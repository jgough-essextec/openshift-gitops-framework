#!/usr/bin/env python3
"""
Bulk update ADR frontmatter to proper YAML format.

This script converts the old format:
    # Title
    **Status:** Proposed
    **Date:** 2025-08-20

To proper YAML frontmatter:
    ---
    status: proposed
    date: "2025-08-20"
    decision-makers: ["Platform Team", "Architecture Team"]
    ---
    # Title
"""

import os
import re
from pathlib import Path


def convert_adr_frontmatter(filepath: Path):
    """Convert ADR to proper YAML frontmatter format."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has YAML frontmatter
    if content.startswith('---'):
        print(f"⏭️  Skipping {filepath.name} - already has YAML frontmatter")
        return False
    
    lines = content.split('\n')
    
    # Extract title (first line starting with #)
    title = None
    title_index = -1
    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line[2:].strip()
            title_index = i
            break
    
    if not title:
        print(f"⚠️  Warning: No title found in {filepath.name}")
        return False
    
    # Extract status and date from bold format
    status = None
    date = None
    lines_to_remove = []
    
    for i, line in enumerate(lines):
        if '**Status:**' in line:
            match = re.search(r'\*\*Status:\*\*\s+(\w+)', line)
            if match:
                status = match.group(1).lower()
                lines_to_remove.append(i)
        
        if '**Date:**' in line:
            match = re.search(r'\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})', line)
            if match:
                date = match.group(1)
                lines_to_remove.append(i)
    
    if not status:
        status = 'proposed'
    
    if not date:
        date = '2025-08-20'
    
    # Build new content with YAML frontmatter
    new_lines = []
    new_lines.append('---')
    new_lines.append(f'status: {status}')
    new_lines.append(f'date: "{date}"')
    new_lines.append('decision-makers: ["Platform Team", "Architecture Team"]')
    new_lines.append('---')
    new_lines.append('')
    
    # Add remaining content (skip title and old status/date lines)
    for i, line in enumerate(lines):
        if i in lines_to_remove:
            continue
        if i >= title_index:
            new_lines.append(line)
    
    # Write back
    new_content = '\n'.join(new_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated {filepath.name}")
    return True


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    adr_dir = repo_root / 'docs' / 'decisions'
    
    if not adr_dir.exists():
        print(f"❌ ADR directory not found: {adr_dir}")
        return
    
    adr_files = sorted(adr_dir.glob('*.md'))
    
    if not adr_files:
        print(f"⚠️  No ADR files found in {adr_dir}")
        return
    
    print(f"Converting {len(adr_files)} ADR files to YAML frontmatter...\n")
    
    updated_count = 0
    for filepath in adr_files:
        if convert_adr_frontmatter(filepath):
            updated_count += 1
    
    print(f"\n✅ Converted {updated_count} ADR files")
    print(f"⏭️  Skipped {len(adr_files) - updated_count} files")
    
    # Regenerate index
    print("\nRegenerating ADR index...")
    os.system('python3 scripts/generate_adr_index.py')


if __name__ == '__main__':
    main()
