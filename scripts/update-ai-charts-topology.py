#!/usr/bin/env python3
"""
Batch update AI application charts to use topology-aware replicas and PDBs
"""

import os
import sys
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent
AI_DIR = REPO_ROOT / "charts" / "applications" / "ai"

# List of AI apps to update
AI_APPS = [
    "open-webui",
    "ollama",
    "litellm"
]

PDB_TEMPLATE = """{{- if .Values.topology.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ .Release.Name }}
  labels:
    app.kubernetes.io/name: {{ .Release.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  minAvailable: {{ .Values.topology.pdb.minAvailable }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Release.Name }}
      app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
"""

def add_replicas_to_statefulset(filepath: Path) -> bool:
    """Add replicas field to StatefulSet spec if not present"""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Check if replicas already exists
    if any('replicas:' in line for line in lines):
        return False

    # Find 'spec:' line and insert replicas after it
    modified = False
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.strip() == 'spec:':
            # Use critical tier for AI apps (they're more important)
            new_lines.append('  replicas: {{ .Values.topology.replicas.critical | default 1 }}\n')
            modified = True
            break

    if modified:
        new_lines.extend(lines[len(new_lines):])
        with open(filepath, 'w') as f:
            f.writelines(new_lines)

    return modified

def create_pdb(filepath: Path) -> bool:
    """Create PodDisruptionBudget template if not exists"""
    if filepath.exists():
        return False

    with open(filepath, 'w') as f:
        f.write(PDB_TEMPLATE)

    return True

def main():
    print("🔄 Updating AI application charts for topology awareness...")
    print()

    updated_count = 0
    skipped_count = 0

    for app in AI_APPS:
        app_dir = AI_DIR / app
        statefulset_file = app_dir / "templates" / "statefulset.yaml"
        pdb_file = app_dir / "templates" / "poddisruptionbudget.yaml"

        if not statefulset_file.exists():
            print(f"⚠️  Skipping {app} (no statefulset.yaml found)")
            skipped_count += 1
            continue

        print(f"📝 Updating {app}...")

        # Add replicas field
        if add_replicas_to_statefulset(statefulset_file):
            print("   ✅ Added replicas field (using critical tier)")
        else:
            print("   ℹ️  replicas field already exists")

        # Create PDB
        if create_pdb(pdb_file):
            print("   ✅ Created PodDisruptionBudget")
        else:
            print("   ℹ️  PodDisruptionBudget already exists")

        updated_count += 1
        print()

    print("✨ Update complete!")
    print()
    print("Summary:")
    print(f"  ✅ Updated: {updated_count} apps")
    print(f"  ⚠️  Skipped: {skipped_count} apps")
    print()
    print("Changes made to each app:")
    print("  1. Added 'replicas: {{ .Values.topology.replicas.critical | default 1 }}' to StatefulSet")
    print("  2. Created templates/poddisruptionbudget.yaml (conditional on topology.pdb.enabled)")
    print()
    print("Note: AI apps use 'critical' replica tier (higher priority than media apps)")

if __name__ == "__main__":
    main()
