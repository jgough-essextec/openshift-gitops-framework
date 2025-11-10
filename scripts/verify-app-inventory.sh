#!/usr/bin/env bash
# Verify that all values-*.yaml files have complete application inventories

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "======================================================================"
echo "Values Files Application Inventory Verification"
echo "======================================================================"
echo

# Define expected apps per domain
declare -A EXPECTED_APPS=(
    ["ai"]=3
    ["media"]=21
    ["homeAutomation"]=4
    ["productivity"]=7
    ["infrastructure"]=5
)

TOTAL_EXPECTED=39  # Sum of all domains

# Check each values file
for values_file in values-*.yaml; do
    # Skip template files
    if [[ "$values_file" == *"template"* ]]; then
        continue
    fi

    echo "Checking: $values_file"
    echo "----------------------------------------"

    # Count app entries in each domain
    for domain in ai media homeAutomation productivity infrastructure; do
        # Count lines with '# - ' pattern (commented apps) and '- ' pattern (enabled apps)
        # within the domain's apps: section
        app_count=$(awk "
            /^  *${domain}:/ { in_domain=1; next }
            in_domain && /^  *apps:/ { in_apps=1; next }
            in_apps && /^  *[a-zA-Z]/ { in_apps=0; in_domain=0 }
            in_apps && /^  *#? *- [a-z]/ { count++ }
            END { print count+0 }
        " "$values_file")

        expected=${EXPECTED_APPS[$domain]}

        if [ "$app_count" -eq "$expected" ]; then
            echo "  ✓ ${domain}: ${app_count}/${expected} apps"
        else
            echo "  ✗ ${domain}: ${app_count}/${expected} apps (MISMATCH!)"
        fi
    done

    echo
done

echo "======================================================================"
echo "Expected Application Counts:"
echo "  AI: ${EXPECTED_APPS[ai]}"
echo "  Media: ${EXPECTED_APPS[media]}"
echo "  Home Automation: ${EXPECTED_APPS[homeAutomation]}"
echo "  Productivity: ${EXPECTED_APPS[productivity]}"
echo "  Infrastructure: ${EXPECTED_APPS[infrastructure]}"
echo "  TOTAL: $TOTAL_EXPECTED"
echo "======================================================================"
