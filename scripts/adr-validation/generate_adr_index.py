#!/usr/bin/env python3
"""
ADR Index Generator for OpenShift-Arch Repository

This script automatically generates the adr-index.md file from ADR files.

Usage:
    python3 scripts/generate_adr_index.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from datetime import datetime


def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """Extract and parse YAML frontmatter."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        return None, content
    
    frontmatter_raw = match.group(1)
    body = content[match.end():]
    
    # Parse simple YAML frontmatter
    frontmatter = {}
    for line in frontmatter_raw.split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"\'')
    
    return frontmatter, body


def get_title(content: str) -> Optional[str]:
    """Extract the main title (H1 heading)."""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None


def parse_adr_number(filename: str) -> int:
    """Extract ADR number from filename."""
    match = re.match(r'^(\d+)-.*\.md$', filename)
    if match:
        return int(match.group(1))
    return -1


def parse_adr_file(filepath: Path) -> Dict:
    """Parse ADR file and extract metadata."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = extract_frontmatter(content)
    title = get_title(body)
    number = parse_adr_number(filepath.name)
    
    return {
        'number': number,
        'filename': filepath.name,
        'title': title or 'Untitled',
        'status': frontmatter.get('status', frontmatter.get('Status', 'unknown')) if frontmatter else 'unknown',
        'date': frontmatter.get('date', frontmatter.get('Date', '')) if frontmatter else '',
        'filepath': filepath
    }


def generate_index(adr_dir: Path, output_file: Path):
    """Generate ADR index markdown file."""
    
    # Get all ADR files
    adr_files = sorted(adr_dir.glob('*.md'))
    
    if not adr_files:
        print(f"⚠️  No ADR files found in {adr_dir}")
        return
    
    # Parse all ADRs
    adrs = []
    for filepath in adr_files:
        try:
            adr_data = parse_adr_file(filepath)
            if adr_data['number'] != -1:
                adrs.append(adr_data)
        except Exception as e:
            print(f"⚠️  Error parsing {filepath.name}: {e}")
    
    # Sort by number
    adrs.sort(key=lambda x: x['number'])
    
    # Generate markdown content
    lines = [
        "# Architecture Decision Records (ADR) Index",
        "",
        "This index is automatically generated. Do not edit manually.",
        "",
        f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  ",
        f"**Total ADRs:** {len(adrs)}",
        "",
        "---",
        "",
        "## All Architecture Decision Records",
        ""
    ]
    
    # Group by status
    by_status = {}
    for adr in adrs:
        status = adr['status'].lower()
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(adr)
    
    # Add status sections
    status_order = ['accepted', 'proposed', 'deprecated', 'superseded', 'rejected', 'unknown']
    status_icons = {
        'accepted': '✅',
        'proposed': '🔄',
        'deprecated': '⚠️',
        'superseded': '🔀',
        'rejected': '❌',
        'unknown': '❓'
    }
    
    for status in status_order:
        if status in by_status:
            icon = status_icons.get(status, '')
            lines.append(f"### {icon} {status.title()}")
            lines.append("")
            
            for adr in by_status[status]:
                date_str = f" ({adr['date']})" if adr['date'] else ""
                lines.append(f"- **[ADR-{adr['number']:03d}](docs/decisions/{adr['filename']})**: {adr['title']}{date_str}")
            
            lines.append("")
    
    # Add complete list
    lines.extend([
        "---",
        "",
        "## Complete List (Chronological)",
        ""
    ])
    
    for adr in adrs:
        status_icon = status_icons.get(adr['status'].lower(), '')
        date_str = f" - {adr['date']}" if adr['date'] else ""
        lines.append(f"{adr['number']:03d}. {status_icon} **[{adr['title']}](docs/decisions/{adr['filename']})** - *{adr['status'].title()}*{date_str}")
    
    lines.extend([
        "",
        "---",
        "",
        "## Legend",
        "",
        "- ✅ **Accepted** - This decision is currently in effect",
        "- 🔄 **Proposed** - This decision is under consideration",
        "- ⚠️ **Deprecated** - This decision has been deprecated but not yet superseded",
        "- 🔀 **Superseded** - This decision has been replaced by a newer decision",
        "- ❌ **Rejected** - This decision was considered but not adopted",
        "",
        "---",
        "",
        "## How to Use This Index",
        "",
        "1. **Browse by Status:** Find ADRs grouped by their current status",
        "2. **Browse Chronologically:** See all ADRs in order of creation",
        "3. **Click Links:** Each ADR title links to the full decision document",
        "",
        "## Creating a New ADR",
        "",
        "1. Use the next sequential number (currently: " + f"{max([a['number'] for a in adrs]) + 1:03d}" + ")",
        "2. Follow the naming convention: `NNN-decision-title.md`",
        "3. Include YAML frontmatter with `status`, `date`, and `decision-makers`",
        "4. Run `python3 scripts/generate_adr_index.py` to update this index",
        "",
        "---",
        "",
        f"*Generated by scripts/generate_adr_index.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    # Write to file
    content = '\n'.join(lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Generated index with {len(adrs)} ADRs")
    print(f"   Output: {output_file}")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    adr_dir = repo_root / 'docs' / 'decisions'
    output_file = repo_root / 'adr-index.md'
    
    if not adr_dir.exists():
        print(f"❌ ADR directory not found: {adr_dir}")
        sys.exit(1)
    
    print("Generating ADR index...\n")
    
    try:
        generate_index(adr_dir, output_file)
        print("\n✅ Index generation complete")
    except Exception as e:
        print(f"\n❌ Error generating index: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
