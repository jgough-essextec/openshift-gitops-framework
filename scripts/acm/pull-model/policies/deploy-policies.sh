#!/bin/bash
set -e

echo "=========================================="
echo "Deploying ACM Policies for Pull Model"
echo "=========================================="
echo ""

# Check we're on hub cluster
CURRENT_CLUSTER=$(oc config current-context 2>/dev/null | grep -o '[^/]*$' || echo "unknown")
echo "Current cluster: $CURRENT_CLUSTER"
echo ""

if [[ "$CURRENT_CLUSTER" != *"hub"* ]]; then
    echo "⚠️  WARNING: You might not be on the hub cluster!"
    echo "Current context: $(oc config current-context)"
    read -p "Continue anyway? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create namespace if not exists
echo "1. Creating open-cluster-management-policies namespace..."
oc create namespace open-cluster-management-policies 2>/dev/null && echo "   ✅ Created" || echo "   ℹ️  Already exists"
echo ""

# Deploy policies in order
echo "2. Deploying ACM policies..."
echo ""

echo "   a) Install GitOps Policy..."
oc apply -f 01-install-gitops-policy.yaml
echo "   ✅ install-openshift-gitops policy created"
echo ""

echo "   b) Bootstrap Application Policy..."
oc apply -f 02-bootstrap-application-policy.yaml
echo "   ✅ bootstrap-cluster-application policy created"
echo ""

echo "   c) Argo RBAC Policy..."
oc apply -f 03-configure-argo-rbac-policy.yaml
echo "   ✅ configure-argocd-rbac policy created"
echo ""

# Wait for policies to be created
echo "3. Waiting for policies to be processed..."
sleep 5
echo ""

# Check policy status
echo "4. Checking policy status..."
echo ""
oc get policy -n open-cluster-management-policies -o wide
echo ""

# Check placement
echo "5. Checking PlacementRule..."
echo ""
oc get placementrule homelab-clusters -n open-cluster-management-policies -o wide
echo ""

# Check which clusters will be targeted
echo "6. Clusters that will be targeted:"
echo ""
oc get managedcluster -l cluster.open-cluster-management.io/clusterset=homelab -o custom-columns=NAME:.metadata.name,AVAILABLE:.status.conditions[?\(@.type==\"ManagedClusterConditionAvailable\"\)].status
echo ""

echo "=========================================="
echo "✅ ACM Policies Deployed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Monitor policy compliance:"
echo "   watch -n 10 'oc get policy -n open-cluster-management-policies -o wide'"
echo ""
echo "2. Check on managed clusters:"
echo "   test  # Switch to test cluster"
echo "   oc get subscription openshift-gitops-operator -n openshift-operators"
echo "   oc get application cluster -n openshift-gitops"
echo ""
echo "3. View in ACM Console:"
echo "   Navigate to: Governance > Policies"
echo ""
echo "4. View detailed policy status:"
echo "   oc describe policy install-openshift-gitops -n open-cluster-management-policies"
echo ""

# Optionally watch compliance
read -p "Watch policy compliance now? (y/N): " watch_now
if [[ "$watch_now" == "y" || "$watch_now" == "Y" ]]; then
    watch -n 10 'oc get policy -n open-cluster-management-policies -o wide'
fi
