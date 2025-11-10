# ACM Multi-Cluster Platform Deployment

This directory contains ApplicationSets and configuration for deploying platform components to managed clusters using Red Hat Advanced Cluster Management (ACM).

## Quick Start

### Push Model (Recommended for Homelab)

```bash
# 1. Deploy ACM configuration
cd acm
./deploy-acm-config.sh

# 2. Create ACM-Argo CD bridge
oc apply -f 05-gitopscluster.yaml

# 3. Deploy platform ApplicationSet
oc apply -f homelab-platform-simple.yaml

# 4. Verify deployment
oc get applicationset -n openshift-gitops | grep homelab
oc get applications -n openshift-gitops | grep test-
```

**See**: `QUICK-START.md` for 5-minute setup guide

### Pull Model (Alternative)

```bash
# Deploy ACM policies to configure managed clusters
cd acm/policies
./deploy-policies.sh
```

**See**: `PULL-MODEL-SETUP.md` for complete pull model guide

## Overview

This directory contains configuration for ACM-based multi-cluster deployments. ACM supports **two deployment models**:

1. **Push Model** (✅ Currently Deployed): Hub cluster pushes applications to managed clusters
2. **Pull Model** (📋 Ready to Deploy): Each cluster pulls its own configuration from Git

See `MODEL-COMPARISON.md` for detailed comparison and decision guide.

## Files

### Push Model Files (Current Setup)

- **`01-managedclusterset.yaml`** - Defines the homelab ClusterSet for grouping managed clusters
- **`02-managedclustersetbinding.yaml`** - Binds the homelab ClusterSet to openshift-gitops namespace
- **`03-placement-platform.yaml`** - Primary placement selecting all homelab clusters
- **`03-placement-examples.yaml`** - Additional placement examples (SNO, multinode, prod, test)
- **`05-gitopscluster.yaml`** - ⭐ ACM-Argo CD bridge (critical for push model)
- **`homelab-platform-simple.yaml`** - ⭐ Working ApplicationSet using clusters generator
- **`04-label-clusters.sh`** - Script to label managed clusters with appropriate tags
- **`deploy-acm-config.sh`** - Automated deployment script for all ACM configuration

### Pull Model Files (Alternative)

- **`policies/`** - ACM Policies for pull-based deployment
  - `01-install-gitops-policy.yaml` - Install GitOps on managed clusters
  - `02-bootstrap-application-policy.yaml` - Create bootstrap Applications
  - `03-configure-argo-rbac-policy.yaml` - Configure RBAC
  - `deploy-policies.sh` - Automated policy deployment

### Documentation

- **`README.md`** - This file - complete ACM guide
- **`QUICK-START.md`** - ⭐ 5-minute push model setup
- **`PULL-MODEL-SETUP.md`** - Complete pull model guide
- **`MODEL-COMPARISON.md`** - ⭐ Compare push vs pull vs hybrid
- **`WORKING-CONFIG.md`** - Technical deep dive of working push setup
- **`DEPLOYMENT-STATUS.md`** - Current deployment status
- **`INDEX.md`** - File index and quick reference
- **`EXTRACTION-SUMMARY.md`** - Configuration extraction details

### ApplicationSet Files

### homelab-platform-applicationset.yaml

Deploys the **entire platform chart** to managed clusters.

**Pros:**

- Simpler - one ApplicationSet for all platform components
- Uses the existing `charts/platform/` chart structure
- Easier to maintain consistency

**Cons:**

- Less flexibility per-cluster
- All-or-nothing deployment
- Harder to customize per cluster

**Use when:** You want all platform components on all clusters with minimal customization

### homelab-platform-components-applicationset.yaml

Deploys **individual platform components** to managed clusters using a matrix generator.

**Pros:**

- Granular control - enable/disable components per cluster
- Easier to customize per-component
- Can filter components based on cluster labels
- Sync waves per component

**Cons:**

- More complex ApplicationSet
- Creates many individual Applications
- Requires understanding of matrix generators

**Use when:** You need different platform components on different clusters

## Prerequisites

1. **ACM installed on hub cluster**

   ```bash
   # Check ACM status
   oc get multiclusterhub -n open-cluster-management
   ```

2. **Managed clusters imported**

   ```bash
   # Check managed clusters
   oc get managedclusters
   ```

3. **ClusterSet created**

   ```bash
   # Check clusterset
   oc get managedclusterset homelab
   ```

4. **Clusters assigned to ClusterSet**

   ```bash
   # Verify cluster labels
   oc get managedclusters --show-labels | grep clusterset=homelab
   ```

5. **Placement created**
   ```bash
   # Check placement
   oc get placement platform-placement-1 -n openshift-gitops -o yaml
   ```

## Deployment

### Option 1: Deploy Full Platform Chart

```bash
# Apply the full platform ApplicationSet
oc apply -f acm/homelab-platform-applicationset.yaml

# Watch ApplicationSet create child Applications
oc get applicationset homelab-platform -n openshift-gitops -w

# Check generated Applications (one per cluster)
oc get applications -n openshift-gitops | grep platform

# Example output:
# prod-platform     Synced   Healthy   ...
# test-platform     Synced   Healthy   ...
```

### Option 2: Deploy Individual Components

```bash
# Apply the component-based ApplicationSet
oc apply -f acm/homelab-platform-components-applicationset.yaml

# Watch ApplicationSet create child Applications
oc get applicationset homelab-platform-components -n openshift-gitops -w

# Check generated Applications (one per cluster per component)
oc get applications -n openshift-gitops | grep -E "prod-|test-"

# Example output:
# prod-external-secrets-operator    Synced   Healthy   ...
# prod-certificates                 Synced   Healthy   ...
# test-external-secrets-operator    Synced   Healthy   ...
# test-certificates                 Synced   Healthy   ...
```

## Verification

### Check Placement Decisions

```bash
# Verify which clusters are selected
oc get placementdecision platform-placement-1-decision-1 -n openshift-gitops -o yaml

# Should show both prod and test clusters
```

### Check Applications on Managed Clusters

```bash
# Switch to managed cluster
sno  # or test

# Check if platform components are deployed
oc get pods -n external-secrets-operator
oc get pods -n certificates
oc get pods -n goldilocks

# Check Argo CD application status
oc get applications -n openshift-gitops
```

## Customization

### Per-Cluster Configuration

To customize configuration per cluster, you have several options:

#### Option 1: Use Cluster Labels

Add labels to managed clusters and conditionally enable components:

```bash
# Label clusters
oc label managedcluster prod storage=truenas gpu=false
oc label managedcluster test storage=synology gpu=false

# Update ApplicationSet to use labels in conditions
```

#### Option 2: Create Separate Placements

Create different placements for different cluster groups:

```yaml
---
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: Placement
metadata:
  name: platform-placement-prod
  namespace: openshift-gitops
spec:
  clusterSets:
    - homelab
  predicates:
    - requiredClusterSelector:
        labelSelector:
          matchLabels:
            name: prod
---
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: Placement
metadata:
  name: platform-placement-test
  namespace: openshift-gitops
spec:
  clusterSets:
    - homelab
  predicates:
    - requiredClusterSelector:
        labelSelector:
          matchLabels:
            name: test
```

Then create separate ApplicationSets referencing each placement.

#### Option 3: Use Values Files Per Cluster

Create cluster-specific values files:

```bash
# Values files are organized in clusters/ directory
clusters/individual-clusters/values-prod.yaml
clusters/individual-clusters/values-test.yaml

# Update ApplicationSet to use values file based on cluster name
```

## Current Setup

Your current configuration:

- **ClusterSet:** `homelab` (with prod and test clusters)
- **Placement:** `platform-placement-1` (selects both clusters)
- **Missing:** ACM-aware ApplicationSet (this directory provides it)

The hub cluster currently uses local ApplicationSets (`hub-platform`) which only deploy to the hub itself. The ApplicationSets in this directory deploy to **managed clusters** instead.

## Comparison: Local vs ACM Deployment

| Aspect            | Local (Current)                      | ACM Multi-Cluster (New)                         |
| ----------------- | ------------------------------------ | ----------------------------------------------- |
| **Management**    | Each cluster self-manages            | Hub cluster manages all                         |
| **Configuration** | Per-cluster values files             | Centralized with cluster labels                 |
| **Argo CD**       | Argo CD on each cluster              | Argo CD on hub only                             |
| **Pros**          | Cluster autonomy, resilient to hub   | Centralized control, consistent deployments     |
| **Cons**          | More complex config per cluster      | Hub becomes single point of control             |
| **Use Case**      | Production, autonomous edge clusters | Development, testing, centralized management    |
| **This Repo**     | ✅ Currently implemented             | ❌ Requires ApplicationSets from this directory |

## Migration Strategy

If you want to migrate from local to ACM deployment:

1. **Test in parallel**: Keep local ApplicationSets, add ACM ApplicationSets
2. **Verify**: Ensure ACM deploys correctly to all clusters
3. **Disable local**: Remove local ApplicationSets from managed clusters
4. **Keep hub local**: Hub cluster should still use local ApplicationSets

**Recommended:** Use **hybrid approach**:

- **Hub cluster**: Local ApplicationSets (self-managed)
- **Managed clusters**: ACM ApplicationSets (hub-managed)

This provides centralized management for edge clusters while keeping the hub autonomous.

## Troubleshooting

### ApplicationSet Not Creating Applications

```bash
# Check ApplicationSet status
oc get applicationset homelab-platform -n openshift-gitops -o yaml

# Look for errors in conditions
# Check if placement decisions exist
oc get placementdecisions -n openshift-gitops

# Verify ACM placement controller is working
oc get pods -n open-cluster-management-hub | grep placement
```

### Applications Not Syncing to Managed Clusters

```bash
# Check if Argo CD can reach managed clusters
oc get secret -n openshift-gitops | grep -E "prod|test"

# Check Argo CD cluster secrets
oc describe secret -n openshift-gitops <cluster-secret>

# Verify managed cluster Argo CD integration
oc get gitopscluster -A
```

### Components Failing on Managed Clusters

```bash
# Switch to managed cluster
test

# Check application status
oc get applications -n openshift-gitops

# Check specific application
oc get application external-secrets-operator -n openshift-gitops -o yaml

# Check pod logs
oc logs -n external-secrets-operator -l app=external-secrets-operator
```

## Best Practices

1. **Start small**: Deploy one component first (external-secrets-operator)
2. **Use sync waves**: Ensure dependencies are deployed in order
3. **Label clusters**: Use labels for conditional deployment
4. **Monitor closely**: Watch first sync to catch issues early
5. **Keep hub local**: Don't use ACM to manage the hub's own components
6. **Test placement**: Verify placement decisions before deploying ApplicationSets

## Next Steps

1. ✅ Review and customize the ApplicationSets
2. ✅ Update values for your specific cluster configurations
3. ⬜ Apply one of the ApplicationSets
4. ⬜ Monitor deployment across clusters
5. ⬜ Verify components are healthy on managed clusters
6. ⬜ Consider creating additional ApplicationSets for application workloads

## Reference

- [ACM Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes)
- [Argo CD ApplicationSet Documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/)
- [Cluster Decision Resource Generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Cluster-Decision-Resource/)
- [Red Hat Validated Patterns](https://validatedpatterns.io/)
