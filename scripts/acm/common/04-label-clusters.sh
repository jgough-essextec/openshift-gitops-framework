#!/bin/bash
# Script to label managed clusters for the homelab clusterset
# Run this after importing clusters to assign them to the homelab clusterset

set -e

echo "🏷️  Labeling managed clusters for homelab clusterset..."
echo ""

# Assign clusters to homelab clusterset
echo "📍 Assigning clusters to homelab clusterset..."
oc label managedcluster prod cluster.open-cluster-management.io/clusterset=homelab --overwrite
oc label managedcluster test cluster.open-cluster-management.io/clusterset=homelab --overwrite

# Add custom labels for filtering
echo ""
echo "🏷️  Adding custom labels..."

# Environment labels
oc label managedcluster prod environment=homelab --overwrite
oc label managedcluster test environment=homelab --overwrite

# Topology labels
oc label managedcluster prod topology=sno --overwrite
oc label managedcluster test topology=sno --overwrite

# Cloud provider labels (adjust as needed)
oc label managedcluster prod cloud=BareMetal --overwrite || true
oc label managedcluster test cloud=BareMetal --overwrite || true

# Region labels (for placement decisions)
oc label managedcluster prod region=edge --overwrite
oc label managedcluster test region=edge --overwrite

echo ""
echo "✅ Cluster labeling complete!"
echo ""
echo "📊 Current cluster labels:"
echo ""
oc get managedclusters prod,test --show-labels
echo ""
echo "🔍 Verify clusterset membership:"
oc get managedclusters -l cluster.open-cluster-management.io/clusterset=homelab
