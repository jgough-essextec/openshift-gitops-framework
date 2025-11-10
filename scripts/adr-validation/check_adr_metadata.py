#!/usr/bin/env python3
"""
ADR Metadata Validator for OpenShift-Arch Repository

This script validates YAML frontmatter metadata in ADRs.

Usage:
    python3 scripts/check_adr_metadata.py [adr_file]
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from datetime import datetime


# Valid status values
VALID_STATUSES = ['proposed', 'accepted', 'rejected', 'deprecated', 'superseded']

# Common typos
STATUS_TYPOS = {
    'superceded': 'superseded',
    'approve': 'accepted',
    'declined': 'rejected'
}


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
    current_key = None
    current_value = []
    
    for line in frontmatter_raw.split('\n'):
        line = line.rstrip()
        
        if not line or line.startswith('#'):
            continue
        
        if ':' in line and not line.startswith(' '):
            # Save previous key-value
            if current_key:
                frontmatter[current_key] = '\n'.join(current_value).strip()
            
            # Parse new key-value
            key, value = line.split(':', 1)
            current_key = key.strip()
            current_value = [value.strip().strip('"\'')]
        elif line.startswith(' ') or line.startswith('-'):
            # Continuation or list item
            current_value.append(line.strip())
    
    # Save last key-value
    if current_key:
        frontmatter[current_key] = '\n'.join(current_value).strip()
    
    return frontmatter, body


def validate_status(status: str) -> Tuple[bool, Optional[str]]:
    """Validate status field."""
    status_lower = status.lower()
    
    # Check for typos
    if status_lower in STATUS_TYPOS:
        return False, f"Status '{status}' should be '{STATUS_TYPOS[status_lower]}'"
    
    # Check if valid
    if status_lower not in VALID_STATUSES:
        return False, f"Invalid status '{status}' (must be one of: {', '.join(VALID_STATUSES)})"
    
    return True, None


def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """Validate date format (YYYY-MM-DD)."""
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    
    if not re.match(date_pattern, date_str):
        return False, f"Date '{date_str}' should be in YYYY-MM-DD format"
    
    # Try to parse the date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, f"Invalid date '{date_str}'"


def validate_metadata(filepath: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate ADR metadata.
    
    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Error reading file: {e}")
        return False, errors, warnings
    
    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)
    
    if not frontmatter:
        warnings.append("No YAML frontmatter found")
        return True, errors, warnings  # Not an error, just a warning
    
    # Validate status (required)
    if 'status' not in frontmatter and 'Status' not in frontmatter:
        errors.append("Missing required field: 'status'")
    else:
        status = frontmatter.get('status', frontmatter.get('Status', ''))
        valid, error = validate_status(status)
        if not valid:
            errors.append(error)
    
    # Validate date (recommended)
    if 'date' not in frontmatter and 'Date' not in frontmatter:
        warnings.append("Missing recommended field: 'date'")
    else:
        date = frontmatter.get('date', frontmatter.get('Date', ''))
        valid, error = validate_date(date)
        if not valid:
            errors.append(error)
    
    # Check for decision-makers (recommended)
    has_decision_makers = any(
        key in frontmatter 
        for key in ['decision-makers', 'decisionMakers', 'decision_makers', 
                    'Decision-makers', 'DecisionMakers', 'Decision_makers']
    )
    if not has_decision_makers:
        warnings.append("Missing recommended field: 'decision-makers'")
    
    passed = len(errors) == 0
    return passed, errors, warnings


def validate_all_metadata(adr_dir: Path) -> Tuple[int, int]:
    """
    Validate metadata for all ADRs.
    
    Returns:
        Tuple of (passed_count, failed_count)
    """
    passed_count = 0
    failed_count = 0
    
    adr_files = sorted(adr_dir.glob('*.md'))
    
    if not adr_files:
        print(f"⚠️  No ADR files found in {adr_dir}")
        return 0, 0
    
    print(f"Validating metadata for {len(adr_files)} ADR files...\n")
    
    for filepath in adr_files:
        passed, errors, warnings = validate_metadata(filepath)
        
        if passed:
            passed_count += 1
            if warnings:
                print(f"⚠️  {filepath.name}")
                for warning in warnings:
                    print(f"    ⚠️  {warning}")
            else:
                print(f"✅ {filepath.name}")
        else:
            failed_count += 1
            print(f"❌ {filepath.name}")
            for error in errors:
                print(f"    ❌ {error}")
            for warning in warnings:
                print(f"    ⚠️  {warning}")
        
        print()
    
    return passed_count, failed_count


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    adr_dir = repo_root / 'docs' / 'decisions'
    
    if len(sys.argv) > 1:
        # Validate specific file
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            sys.exit(1)
        
        passed, errors, warnings = validate_metadata(filepath)
        
        print(f"Validating metadata for {filepath.name}...\n")
        
        if passed:
            print("✅ Validation passed")
        else:
            print("❌ Validation failed")
        
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  ❌ {error}")
        
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  ⚠️  {warning}")
        
        sys.exit(0 if passed else 1)
    
    else:
        # Validate all ADRs
        if not adr_dir.exists():
            print(f"❌ ADR directory not found: {adr_dir}")
            sys.exit(1)
        
        passed_count, failed_count = validate_all_metadata(adr_dir)
        
        print("=" * 60)
        print(f"Metadata validation complete: {passed_count} passed, {failed_count} failed")
        print("=" * 60)
        
        sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()
