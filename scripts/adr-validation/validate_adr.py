#!/usr/bin/env python3
"""
ADR Structure Validator for OpenShift-Arch Repository

This script validates that ADRs follow the MADR (Markdown Architectural Decision Records)
structure and OpenShift-Arch conventions.

Usage:
    python3 scripts/validate_adr.py [adr_file]
    
If no file is specified, validates all ADRs in docs/decisions/
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# MADR required sections
REQUIRED_SECTIONS = [
    "Context",
    "Decision",
    "Consequences"
]

# Recommended sections for completeness
RECOMMENDED_SECTIONS = [
    "Decision Drivers",
    "Considered Options",
    "Pros and Cons of the Options"
]

# Minimum word count for substantial content
MIN_WORD_COUNT = 100


def read_file(filepath: Path) -> str:
    """Read file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return ""


def extract_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """Extract YAML frontmatter if present."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if match:
        frontmatter_raw = match.group(1)
        body = content[match.end():]
        
        # Parse simple YAML frontmatter
        frontmatter = {}
        for line in frontmatter_raw.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')
        
        return frontmatter, body
    
    return None, content


def get_title(content: str) -> Optional[str]:
    """Extract the main title (H1 heading)."""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None


def get_sections(content: str) -> List[str]:
    """Extract all section headings (H2 and H3)."""
    sections = []
    lines = content.split('\n')
    for line in lines:
        if line.startswith('## ') or line.startswith('### '):
            # Remove markdown heading symbols
            section = re.sub(r'^#+\s+', '', line).strip()
            sections.append(section)
    return sections


def count_words(content: str) -> int:
    """Count words in content (excluding frontmatter and code blocks)."""
    # Remove frontmatter
    _, body = extract_frontmatter(content)
    
    # Remove code blocks
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    
    # Remove markdown formatting
    body = re.sub(r'[#*`\[\]()]', '', body)
    
    # Count words
    words = body.split()
    return len(words)


def validate_adr_structure(filepath: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate ADR structure.
    
    Returns:
        Tuple of (passed, errors, warnings)
    """
    errors = []
    warnings = []
    
    content = read_file(filepath)
    if not content:
        errors.append("File is empty or unreadable")
        return False, errors, warnings
    
    # Check for frontmatter
    frontmatter, body = extract_frontmatter(content)
    if not frontmatter:
        warnings.append("No YAML frontmatter found (recommended: status, date, decision-makers)")
    else:
        # Validate frontmatter fields
        if 'status' not in frontmatter:
            warnings.append("Missing 'status' in frontmatter")
        if 'date' not in frontmatter:
            warnings.append("Missing 'date' in frontmatter")
        if 'decision-makers' not in frontmatter and 'decisionMakers' not in frontmatter:
            warnings.append("Missing 'decision-makers' in frontmatter")
    
    # Check for title
    title = get_title(body)
    if not title:
        errors.append("Missing title (H1 heading)")
    else:
        # Check if title contains ADR number (should not)
        if re.search(r'ADR[-\s]?\d+', title, re.IGNORECASE):
            warnings.append(f"Title contains ADR number: '{title}' (numbers should be in filename only)")
    
    # Check for required sections
    sections = get_sections(body)
    for required in REQUIRED_SECTIONS:
        # Flexible matching (partial matches OK)
        if not any(required.lower() in section.lower() for section in sections):
            errors.append(f"Missing required section: '{required}'")
    
    # Check for recommended sections
    for recommended in RECOMMENDED_SECTIONS:
        if not any(recommended.lower() in section.lower() for section in sections):
            warnings.append(f"Missing recommended section: '{recommended}'")
    
    # Check word count
    word_count = count_words(content)
    if word_count < MIN_WORD_COUNT:
        warnings.append(f"Content is short ({word_count} words, recommended: >{MIN_WORD_COUNT})")
    
    passed = len(errors) == 0
    return passed, errors, warnings


def validate_all_adrs(adr_dir: Path) -> Tuple[int, int]:
    """
    Validate all ADRs in directory.
    
    Returns:
        Tuple of (passed_count, failed_count)
    """
    passed_count = 0
    failed_count = 0
    
    adr_files = sorted(adr_dir.glob('*.md'))
    
    if not adr_files:
        print(f"⚠️  No ADR files found in {adr_dir}")
        return 0, 0
    
    print(f"Validating {len(adr_files)} ADR files...\n")
    
    for filepath in adr_files:
        passed, errors, warnings = validate_adr_structure(filepath)
        
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
        
        passed, errors, warnings = validate_adr_structure(filepath)
        
        print(f"Validating {filepath.name}...\n")
        
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
        
        passed_count, failed_count = validate_all_adrs(adr_dir)
        
        print("=" * 60)
        print(f"Validation complete: {passed_count} passed, {failed_count} failed")
        print("=" * 60)
        
        sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()
