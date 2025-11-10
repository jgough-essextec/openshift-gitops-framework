#!/bin/bash
# Sync role templates across all topology roles
# This ensures sno, compact, and full roles have identical ApplicationSet deployers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ROLES_DIR="$REPO_ROOT/roles"

SOURCE_ROLE="sno"
TARGET_ROLES=("compact" "full")

echo "🔄 Syncing role templates from $SOURCE_ROLE to topology roles..."
echo ""

# Verify source role exists
if [ ! -d "$ROLES_DIR/$SOURCE_ROLE/templates" ]; then
    echo "❌ Error: Source role templates not found: $ROLES_DIR/$SOURCE_ROLE/templates"
    exit 1
fi

# Sync to each target role
for role in "${TARGET_ROLES[@]}"; do
    if [ ! -d "$ROLES_DIR/$role" ]; then
        echo "⚠️  Warning: Target role not found: $ROLES_DIR/$role (skipping)"
        continue
    fi

    echo "📋 Syncing to roles/$role/templates/..."

    # Remove existing templates and copy fresh from source
    rm -rf "$ROLES_DIR/$role/templates"
    cp -r "$ROLES_DIR/$SOURCE_ROLE/templates" "$ROLES_DIR/$role/templates"

    echo "✅ Synced roles/$role/"
    echo ""
done

echo "✨ Sync complete!"
echo ""
echo "📝 Note: This syncs only templates/ directories."
echo "   Each role's values.yaml contains topology-specific defaults and should NOT be synced."
echo ""
echo "Modified roles:"
for role in "${TARGET_ROLES[@]}"; do
    if [ -d "$ROLES_DIR/$role" ]; then
        echo "  - roles/$role/templates/"
    fi
done
