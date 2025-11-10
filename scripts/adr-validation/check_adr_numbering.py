#!/usr/bin/env python3
"""
ADR Numbering Validator for OpenShift-Arch Repository

This script validates that ADRs follow proper sequential numbering conventions.

Usage:
    python3 scripts/check_adr_numbering.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def parse_adr_number(filename: str) -> int:
    """Extract ADR number from filename."""
    match = re.match(r'^(\d+)-.*\.md$', filename)
    if match:
        return int(match.group(1))
    return -1


def validate_adr_numbering(adr_dir: Path) -> Tuple[bool, List[str]]:
    """
    Validate ADR numbering sequence.

    Returns:
        Tuple of (passed, errors)
    """
    errors = []

    # Get all ADR files (exclude INDEX.md, template.md, validate-adr.sh)
    adr_files = sorted([f for f in adr_dir.glob('*.md')
                        if f.name not in ['INDEX.md', 'template.md', 'validate-adr.sh']])

    if not adr_files:
        errors.append(f"No ADR files found in {adr_dir}")
        return False, errors

    # Extract numbers and filenames
    adr_numbers = []
    for filepath in adr_files:
        number = parse_adr_number(filepath.name)
        if number == -1:
            errors.append(f"Invalid filename format: {filepath.name} (expected: NNN-title.md or NNNN-title.md)")
        else:
            adr_numbers.append((number, filepath.name))

    # Check for duplicates
    numbers = [n for n, _ in adr_numbers]
    duplicates = set([n for n in numbers if numbers.count(n) > 1])
    if duplicates:
        for dup in sorted(duplicates):
            files = [f for n, f in adr_numbers if n == dup]
            errors.append(f"Duplicate ADR number {dup:04d} found in: {', '.join(files)}")

    # Check for gaps in sequence
    if adr_numbers:
        adr_numbers.sort()
        expected = 0  # Start from 0000
        for number, filename in adr_numbers:
            if number != expected:
                if number > expected:
                    errors.append(f"Gap in sequence: missing ADR {expected:04d} (found {number:04d} - {filename})")
            expected = number + 1

    passed = len(errors) == 0
    return passed, errors


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    adr_dir = repo_root / 'docs' / 'decisions'

    if not adr_dir.exists():
        print(f"❌ ADR directory not found: {adr_dir}")
        sys.exit(1)

    print("Checking ADR numbering sequence...\n")

    passed, errors = validate_adr_numbering(adr_dir)

    if passed:
        print("✅ ADR numbering is valid")

        # Show the sequence
        adr_files = sorted([f for f in adr_dir.glob('*.md')
                            if f.name not in ['INDEX.md', 'template.md', 'validate-adr.sh']])
        numbers = [(parse_adr_number(f.name), f.name) for f in adr_files]
        numbers = [(n, f) for n, f in numbers if n != -1]
        numbers.sort()

        if numbers:
            print(f"\nFound {len(numbers)} ADRs:")
            for number, filename in numbers:
                print(f"  {number:04d} - {filename}")
    else:
        print("❌ ADR numbering validation failed\n")
        for error in errors:
            print(f"  ❌ {error}")

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
