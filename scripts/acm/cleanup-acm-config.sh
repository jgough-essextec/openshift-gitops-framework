#!/bin/bash
# ACM Configuration Cleanup Script
# Removes ACM ApplicationSets, Placements, Bindings, and ClusterSets

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧹 Cleaning up ACM Configuration"
echo "=================================="
echo ""

# Warning
echo "⚠️  WARNING: This will remove:"
echo "   - All homelab ApplicationSets"
echo "   - All Applications deployed to managed clusters"
echo "   - Placements"
echo "   - ManagedClusterSetBinding"
echo "   - ManagedClusterSet (unless clusters are still assigned)"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 0
fi
echo ""

# Step 1: Delete ApplicationSets
echo "🗑️  Step 1: Deleting ApplicationSets..."
oc delete applicationset homelab-platform -n openshift-gitops --ignore-not-found=true
oc delete applicationset homelab-platform-components -n openshift-gitops --ignore-not-found=true
echo "✅ ApplicationSets deleted"
echo ""

# Wait for Applications to be cleaned up
echo "⏳ Waiting for Applications to be cleaned up..."
sleep 5

# Step 2: Delete Placements
echo "🗑️  Step 2: Deleting Placements..."
oc delete placement platform-placement-1 -n openshift-gitops --ignore-not-found=true
oc delete placement platform-placement-sno -n openshift-gitops --ignore-not-found=true
oc delete placement platform-placement-multinode -n openshift-gitops --ignore-not-found=true
oc delete placement platform-placement-prod -n openshift-gitops --ignore-not-found=true
oc delete placement platform-placement-test -n openshift-gitops --ignore-not-found=true
echo "✅ Placements deleted"
echo ""

# Step 3: Delete ManagedClusterSetBinding
echo "🗑️  Step 3: Deleting ManagedClusterSetBinding..."
oc delete managedclustersetbinding homelab -n openshift-gitops --ignore-not-found=true
echo "✅ ManagedClusterSetBinding deleted"
echo ""

# Step 4: Remove cluster labels
echo "🏷️  Step 4: Removing cluster labels..."
read -p "Remove clusterset labels from managed clusters? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    oc label managedcluster prod cluster.open-cluster-management.io/clusterset- --ignore-not-found=true
    oc label managedcluster test cluster.open-cluster-management.io/clusterset- --ignore-not-found=true
    echo "✅ Cluster labels removed"
else
    echo "⏭️  Skipping cluster label removal"
fi
echo ""

# Step 5: Delete ManagedClusterSet
echo "🗑️  Step 5: Deleting ManagedClusterSet..."
oc delete managedclusterset homelab --ignore-not-found=true --wait=false
echo "✅ ManagedClusterSet deletion initiated"
echo ""

# Verification
echo "🔍 Verifying cleanup..."
echo ""

echo "📊 Remaining ApplicationSets:"
oc get applicationset -n openshift-gitops | grep homelab || echo "  None found ✅"
echo ""

echo "🎯 Remaining Placements:"
oc get placement -n openshift-gitops -l app=platform || echo "  None found ✅"
echo ""

echo "🔗 Remaining ClusterSetBindings:"
oc get managedclustersetbinding homelab -n openshift-gitops 2>/dev/null || echo "  None found ✅"
echo ""

echo "📦 ManagedClusterSet status:"
oc get managedclusterset homelab 2>/dev/null || echo "  Deleted ✅"
echo ""

echo "=================================="
echo "✅ ACM Configuration Cleanup Complete!"
echo ""
echo "💡 To redeploy, run:"
echo "   ./acm/deploy-acm-config.sh"
