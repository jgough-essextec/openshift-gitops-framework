#!/bin/bash
# Script to verify an app exists in all cluster ApplicationSets
# Usage: ./scripts/verify-app-in-all-clusters.sh <app-name> <domain>

set -e

APP_NAME="${1}"
DOMAIN="${2}"

if [ -z "$APP_NAME" ] || [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <app-name> <domain>"
    echo ""
    echo "Example: $0 paperless-ai productivity"
    echo ""
    echo "Domains: ai, media, productivity, home-automation, base, security, storage, tweaks"
    exit 1
fi

echo "============================================"
echo "Verifying app: $APP_NAME"
echo "Domain: $DOMAIN"
echo "============================================"
echo ""

CLUSTERS=("sno" "hub" "test" "template")
MISSING=0
FOUND=0

for cluster in "${CLUSTERS[@]}"; do
    FILE="roles/$cluster/templates/$DOMAIN.yaml"

    if [ ! -f "$FILE" ]; then
        echo "❌ $cluster: ApplicationSet file not found: $FILE"
        MISSING=$((MISSING + 1))
        continue
    fi

    # Check for app entry (commented or uncommented)
    if grep -q "name: $APP_NAME" "$FILE" 2>/dev/null; then
        # Check if it's commented
        if grep "name: $APP_NAME" "$FILE" | grep -q "^[[:space:]]*#"; then
            echo "✓  $cluster: Found (commented)"
        else
            echo "✅ $cluster: Found (enabled)"
        fi
        FOUND=$((FOUND + 1))
    else
        echo "❌ $cluster: MISSING from $FILE"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
echo "============================================"
echo "Summary: $FOUND found, $MISSING missing out of ${#CLUSTERS[@]} clusters"
echo "============================================"

if [ $MISSING -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: App is not present in all clusters!"
    echo "Please add to missing clusters (can be commented if not deploying)"
    exit 1
else
    echo ""
    echo "✅ SUCCESS: App exists in all cluster roles"
    exit 0
fi
