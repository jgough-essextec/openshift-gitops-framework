#!/bin/bash
# ACM Configuration Deployment Script
# Deploys ManagedClusterSet, Binding, and Placements for homelab clusters

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Deploying ACM Configuration for Homelab"
echo "=========================================="
echo ""

# Check if we're on the hub cluster
if ! oc get multiclusterhub -n open-cluster-management &>/dev/null; then
    echo "❌ ERROR: ACM not detected. This script must run on the hub cluster."
    echo ""
    echo "💡 Switch to hub cluster: hub"
    exit 1
fi

echo "✅ ACM detected on hub cluster"
echo ""

# Step 1: Create ManagedClusterSet
echo "📦 Step 1: Creating ManagedClusterSet 'homelab'..."
if oc get managedclusterset homelab &>/dev/null; then
    echo "⚠️  ManagedClusterSet 'homelab' already exists, skipping..."
else
    oc apply -f "$SCRIPT_DIR/common/01-managedclusterset.yaml"
    echo "✅ ManagedClusterSet 'homelab' created"
fi
echo ""

# Step 2: Create ManagedClusterSetBinding
echo "🔗 Step 2: Creating ManagedClusterSetBinding in openshift-gitops namespace..."
if oc get managedclustersetbinding homelab -n openshift-gitops &>/dev/null; then
    echo "⚠️  ManagedClusterSetBinding 'homelab' already exists, skipping..."
else
    oc apply -f "$SCRIPT_DIR/common/02-managedclustersetbinding.yaml"
    echo "✅ ManagedClusterSetBinding 'homelab' created"
fi
echo ""

# Step 3: Create Placements
echo "🎯 Step 3: Creating Placement resources..."
oc apply -f "$SCRIPT_DIR/common/03-placement-platform.yaml"
echo "✅ Placement 'platform-placement-1' created/updated"
echo ""

# Optional: Create example placements
read -p "📝 Create additional placement examples (SNO, multinode, prod, test)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    oc apply -f "$SCRIPT_DIR/03-placement-examples.yaml"
    echo "✅ Example placements created"
else
    echo "⏭️  Skipping example placements"
fi
echo ""

# Step 4: Verify deployment
echo "🔍 Step 4: Verifying deployment..."
echo ""

echo "📊 ManagedClusterSet status:"
oc get managedclusterset homelab -o custom-columns=NAME:.metadata.name,SELECTOR:.spec.clusterSelector.selectorType,CLUSTERS:.status.conditions[0].message
echo ""

echo "🔗 ManagedClusterSetBinding status:"
oc get managedclustersetbinding homelab -n openshift-gitops
echo ""

echo "🎯 Placement status:"
oc get placement -n openshift-gitops -l app=platform
echo ""

echo "📋 Placement decisions:"
oc get placementdecisions -n openshift-gitops
echo ""

# Step 5: Check if clusters are labeled
echo "🏷️  Step 5: Checking cluster labels..."
if oc get managedclusters -l cluster.open-cluster-management.io/clusterset=homelab &>/dev/null; then
    CLUSTER_COUNT=$(oc get managedclusters -l cluster.open-cluster-management.io/clusterset=homelab --no-headers | wc -l)
    echo "✅ Found $CLUSTER_COUNT clusters in homelab clusterset:"
    oc get managedclusters -l cluster.open-cluster-management.io/clusterset=homelab -o custom-columns=NAME:.metadata.name,TOPOLOGY:.metadata.labels.topology,ENVIRONMENT:.metadata.labels.environment
    echo ""
else
    echo "⚠️  No clusters found in homelab clusterset"
    echo ""
    echo "💡 Run the labeling script to assign clusters:"
    echo "   ./acm/04-label-clusters.sh"
    echo ""
fi

echo "=========================================="
echo "✅ ACM Configuration Deployment Complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Label your managed clusters (if not done):"
echo "      ./acm/common/04-label-clusters.sh"
echo ""
echo "   2. Choose deployment model:"
echo ""
echo "      PUSH MODEL (Hub pushes to clusters):"
echo "      cd acm/push-model"
echo "      oc apply -f 05-gitopscluster.yaml"
echo "      sleep 15"
echo "      oc apply -f homelab-platform-simple.yaml"
echo ""
echo "      PULL MODEL (Clusters pull from Git):"
echo "      cd acm/pull-model/policies"
echo "      bash deploy-policies.sh"
echo ""
echo "   3. Verify placement decisions:"
echo "      oc get placementdecision platform-placement-1-decision-1 -n openshift-gitops -o yaml"
echo ""
echo "   4. Check ApplicationSet status (push model):"
echo "      oc get applicationset -n openshift-gitops"
echo ""
