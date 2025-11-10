#!/usr/bin/env python3
"""
Cross-Reference Validator for OpenShift-Arch Repository

This script validates that internal markdown links are not broken.

Usage:
    python3 scripts/validate_cross_refs.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set, Optional
from urllib.parse import urlparse


def find_markdown_files(root_dir: Path) -> List[Path]:
    """Find all markdown files in repository."""
    markdown_files = []
    
    # Skip certain directories
    skip_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__'}
    
    for path in root_dir.rglob('*.md'):
        # Check if any parent directory should be skipped
        if not any(skip in path.parts for skip in skip_dirs):
            markdown_files.append(path)
    
    return markdown_files


def extract_links(content: str, filepath: Path) -> List[Tuple[str, int]]:
    """
    Extract all markdown links from content.
    
    Returns list of (link_target, line_number) tuples.
    """
    links = []
    
    # Match markdown links: [text](url)
    # Also match reference-style links: [text][ref]
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    lines = content.split('\n')
    for i, line in enumerate(lines, start=1):
        matches = re.finditer(link_pattern, line)
        for match in matches:
            link_target = match.group(2)
            links.append((link_target, i))
    
    return links


def is_internal_link(link: str) -> bool:
    """Check if link is internal (not external URL)."""
    # Skip external URLs
    if link.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
        return False
    
    # Skip anchors only
    if link.startswith('#'):
        return False
    
    # Skip special URIs
    if link.startswith(('vscode:', 'file:', 'data:')):
        return False
    
    return True


def resolve_link(source_file: Path, link_target: str, repo_root: Path) -> Tuple[bool, Optional[Path]]:
    """
    Resolve a link target to an actual file path.
    
    Returns (exists, resolved_path).
    """
    # Remove anchor if present
    if '#' in link_target:
        link_target = link_target.split('#')[0]
    
    # Remove query parameters if present
    if '?' in link_target:
        link_target = link_target.split('?')[0]
    
    if not link_target:
        return True, None  # Just an anchor, consider valid
    
    # Handle absolute paths from repo root
    if link_target.startswith('/'):
        target_path = repo_root / link_target.lstrip('/')
    else:
        # Relative path from source file directory
        target_path = source_file.parent / link_target
    
    # Resolve to absolute path
    try:
        target_path = target_path.resolve()
    except Exception:
        return False, None
    
    # Check if file exists
    exists = target_path.exists()
    return exists, target_path if exists else None


def validate_file_links(filepath: Path, repo_root: Path) -> Tuple[int, List[str]]:
    """
    Validate all links in a file.
    
    Returns (valid_count, errors).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, [f"Error reading file: {e}"]
    
    links = extract_links(content, filepath)
    internal_links = [(link, line) for link, line in links if is_internal_link(link)]
    
    errors = []
    valid_count = 0
    
    for link_target, line_num in internal_links:
        exists, resolved_path = resolve_link(filepath, link_target, repo_root)
        
        if not exists:
            rel_path = filepath.relative_to(repo_root)
            errors.append(f"{rel_path}:{line_num} - Broken link: [{link_target}]")
        else:
            valid_count += 1
    
    return valid_count, errors


def validate_all_links(repo_root: Path) -> Tuple[int, int, List[str]]:
    """
    Validate links in all markdown files.
    
    Returns (total_files, total_valid_links, all_errors).
    """
    markdown_files = find_markdown_files(repo_root)
    
    if not markdown_files:
        return 0, 0, ["No markdown files found"]
    
    all_errors = []
    total_valid_links = 0
    
    print(f"Checking {len(markdown_files)} markdown files for broken links...\n")
    
    for filepath in markdown_files:
        valid_count, errors = validate_file_links(filepath, repo_root)
        total_valid_links += valid_count
        
        if errors:
            all_errors.extend(errors)
    
    return len(markdown_files), total_valid_links, all_errors


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    
    print("Cross-Reference Validation")
    print("=" * 60)
    print()
    
    total_files, total_valid_links, errors = validate_all_links(repo_root)
    
    if errors:
        print(f"❌ Found {len(errors)} broken link(s):\n")
        for error in errors:
            print(f"  ❌ {error}")
        print()
    
    print("=" * 60)
    print(f"Checked {total_files} files")
    print(f"Valid internal links: {total_valid_links}")
    print(f"Broken links: {len(errors)}")
    print("=" * 60)
    
    if errors:
        print("\n❌ Cross-reference validation failed")
        sys.exit(1)
    else:
        print("\n✅ Cross-reference validation passed")
        sys.exit(0)


if __name__ == '__main__':
    main()
