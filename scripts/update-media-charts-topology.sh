#!/bin/bash
# Batch update media application charts to use topology-aware replicas and PDBs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MEDIA_DIR="$REPO_ROOT/charts/applications/media"

# List of media apps to update
MEDIA_APPS=(
    "sonarr"
    "radarr"
    "prowlarr"
    "overseerr"
    "sabnzbd"
    "bazarr"
    "tautulli"
    "readarr"
    "lidarr"
    "jellyfin"
    "jellyseerr"
    "kavita"
    "metube"
    "pinchflat"
    "posterizarr"
    "huntarr"
    "gaps"
    "kapowarr"
    "flaresolverr"
)

PDB_TEMPLATE='{{- if .Values.topology.pdb.enabled }}
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
'

echo "🔄 Updating media application charts for topology awareness..."
echo ""

updated_count=0
skipped_count=0

for app in "${MEDIA_APPS[@]}"; do
    APP_DIR="$MEDIA_DIR/$app"
    STATEFULSET_FILE="$APP_DIR/templates/statefulset.yaml"
    PDB_FILE="$APP_DIR/templates/poddisruptionbudget.yaml"

    if [ ! -f "$STATEFULSET_FILE" ]; then
        echo "⚠️  Skipping $app (no statefulset.yaml found)"
        ((skipped_count++))
        continue
    fi

    echo "📝 Updating $app..."

    # Add replicas field if not present
    if grep -q "^  replicas:" "$STATEFULSET_FILE"; then
        echo "   ℹ️  replicas field already exists"
    else
        # Insert replicas after 'spec:' line
        sed -i '/^spec:/a\  replicas: {{ .Values.topology.replicas.default | default 1 }}' "$STATEFULSET_FILE"
        echo "   ✅ Added replicas field"
    fi

    # Create PDB if not exists
    if [ -f "$PDB_FILE" ]; then
        echo "   ℹ️  PodDisruptionBudget already exists"
    else
        echo "$PDB_TEMPLATE" > "$PDB_FILE"
        echo "   ✅ Created PodDisruptionBudget"
    fi

    ((updated_count++))
    echo ""
done

echo "✨ Update complete!"
echo ""
echo "Summary:"
echo "  ✅ Updated: $updated_count apps"
echo "  ⚠️  Skipped: $skipped_count apps"
echo ""
echo "Changes made to each app:"
echo "  1. Added 'replicas: {{ .Values.topology.replicas.default | default 1 }}' to StatefulSet"
echo "  2. Created templates/poddisruptionbudget.yaml (conditional on topology.pdb.enabled)"
