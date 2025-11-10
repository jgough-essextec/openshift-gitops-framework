# ACM Configuration Extraction Summary

This document summarizes the ACM configuration extracted from your hub cluster deployment.

## Extracted Configuration

### Date: November 7, 2025

### Source Cluster: hub.roybales.com

The following configuration was extracted from your running ACM deployment and converted into reusable YAML files.

## Configuration Details

### 1. ManagedClusterSet: homelab

```yaml
apiVersion: cluster.open-cluster-management.io/v1beta2
kind: ManagedClusterSet
metadata:
  name: homelab
spec:
  clusterSelector:
    selectorType: ExclusiveClusterSetLabel
```

- **Type**: ExclusiveClusterSetLabel (requires explicit cluster assignment)
- **Status**: 2 clusters selected (prod, test)
- **Submariner**: Enabled with homelab-broker namespace

### 2. ManagedClusterSetBinding

```yaml
apiVersion: cluster.open-cluster-management.io/v1beta2
kind: ManagedClusterSetBinding
metadata:
  name: homelab
  namespace: openshift-gitops
spec:
  clusterSet: homelab
```

- **Namespace**: openshift-gitops
- **Purpose**: Allows Argo CD to deploy to homelab clusters

### 3. Placement: platform-placement-1

```yaml
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: Placement
metadata:
  name: platform-placement-1
  namespace: openshift-gitops
spec:
  clusterSets: [homelab]
  predicates:
    - requiredClusterSelector:
        labelSelector: {}
```

- **ClusterSet**: homelab
- **Selector**: All clusters (empty labelSelector)
- **Decisions**: 2 clusters selected (prod, test)
- **Status**: AllDecisionsScheduled

### 4. Managed Clusters

**test cluster (Active in homelab clusterset):**

- ClusterSet: homelab
- OpenShift Version: 4.20.2
- Vendor: OpenShift
- Cloud: Other (BareMetal)
- Topology: sno
- Environment: homelab
- Custom Labels: ✅ Labeled
- ACM Integration: ✅ GitOpsCluster created
- Platform Deployment: ✅ Active (8 components)

**prod cluster (Not in homelab clusterset):**

- Currently removed from homelab clusterset for testing
- Will be added back after validation

## Files Created

### Core Configuration Files (Apply in order)

1. **`01-managedclusterset.yaml`** - ClusterSet definition
2. **`02-managedclustersetbinding.yaml`** - Binding to openshift-gitops
3. **`03-placement-platform.yaml`** - Primary placement for all clusters
4. **`03-placement-examples.yaml`** - Additional placement examples

### ApplicationSet Files

- **`homelab-platform-applicationset.yaml`** - Full platform chart deployment
- **`homelab-platform-applicationset-template.yaml`** - Editable template
- **`homelab-platform-components-applicationset.yaml`** - Individual components
- **`homelab-platform-components-applicationset-template.yaml`** - Editable template

### Automation Scripts

- **`deploy-acm-config.sh`** - Automated deployment script
- **`04-label-clusters.sh`** - Cluster labeling script
- **`cleanup-acm-config.sh`** - Cleanup script

### Documentation

- **`README.md`** - Complete guide
- **`INDEX.md`** - File index and quick reference
- **`EXTRACTION-SUMMARY.md`** - This file

## Current State vs Desired State

### ✅ Successfully Deployed

- ACM installed and running on hub cluster
- MultiCluster Engine deployed
- Managed cluster imported (test)
- ManagedClusterSet created (homelab)
- ManagedClusterSetBinding created
- Placement created and selecting test cluster
- PlacementDecision generated
- GitOpsCluster created for ACM-Argo CD integration
- ApplicationSet deployed (homelab-platform-simple)
- **8 Platform components deploying to test cluster:**
  - external-secrets-operator
  - certificates
  - openshift-nfd
  - vertical-pod-autoscaler
  - goldilocks
  - gatus
  - generic-device-plugin
  - snapshot-finalizer-remover

### 🎯 Current Status

**ACM → Argo CD Integration: ✅ WORKING**

The hub cluster is successfully managing platform deployments to the test cluster via ACM.

### Next Steps

1. **Monitor test cluster deployments**:

   ```bash
   oc get applications.argoproj.io -n openshift-gitops | grep test-
   ```

2. **Once validated, add prod cluster**:

   ```bash
   oc label managedcluster prod cluster.open-cluster-management.io/clusterset=homelab
   ```

3. **Verify all clusters**:
   ```bash
   oc get placementdecision platform-placement-1-decision-1 -n openshift-gitops -o jsonpath='{.status.decisions[*].clusterName}'
   ```

## Deployment Architecture

### Current (Local)

```
Hub Cluster
  └─ hub-platform ApplicationSet
      └─ Platform Applications (hub only)

Prod Cluster
  └─ prod-platform ApplicationSet
      └─ Platform Applications (prod only)

Test Cluster
  └─ test-platform ApplicationSet
      └─ Platform Applications (test only)
```

Each cluster manages itself independently.

### With ACM (After Applying ApplicationSet)

```
Hub Cluster
  ├─ hub-platform ApplicationSet (local)
  │   └─ Platform Applications (hub only)
  │
  └─ homelab-platform ApplicationSet (ACM)
      ├─ prod-platform Application
      │   └─ Platform Components → Prod Cluster
      └─ test-platform Application
          └─ Platform Components → Test Cluster
```

Hub cluster manages platform deployments for all clusters.

## Recommendations

### For Homelab Use

1. **Use component-based ApplicationSet** - More flexibility
2. **Label clusters appropriately** - Enables conditional deployment
3. **Start with test cluster** - Verify before deploying to prod
4. **Keep hub local** - Don't use ACM to manage hub's own components
5. **Use Basic availability** - Lower resource usage

### For Production Use

1. **Use full platform chart** - Consistency across clusters
2. **Implement policies** - Enforce security and compliance
3. **Enable observability** - Monitor multi-cluster deployments
4. **Use High availability** - For ACM components
5. **Regular backups** - Export ACM configuration regularly

## Backup Instructions

To backup your ACM configuration:

```bash
# Export all ACM resources
oc get managedclusterset homelab -o yaml > backup-clusterset.yaml
oc get managedclustersetbinding homelab -n openshift-gitops -o yaml > backup-binding.yaml
oc get placement -n openshift-gitops -l app=platform -o yaml > backup-placements.yaml
oc get applicationset -n openshift-gitops -o yaml | grep -A 200 "name: homelab" > backup-applicationsets.yaml

# Save to Git
git add backup-*.yaml
git commit -m "Backup ACM configuration"
git push
```

## Recovery Instructions

If ACM needs to be redeployed:

```bash
# 1. Ensure ACM is installed
oc get multiclusterhub -n open-cluster-management

# 2. Deploy saved configuration
./acm/deploy-acm-config.sh

# 3. Label clusters
./acm/04-label-clusters.sh

# 4. Deploy ApplicationSets
oc apply -f acm/homelab-platform-applicationset.yaml

# 5. Verify
oc get placementdecision -n openshift-gitops
oc get applications -n openshift-gitops | grep -E "prod-|test-"
```

## Support

- **Documentation**: See `acm/README.md` for detailed guide
- **File Index**: See `acm/INDEX.md` for file reference
- **Troubleshooting**: Check README troubleshooting section
- **ACM Docs**: https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes

---

**Generated**: November 7, 2025
**Source**: hub.roybales.com
**ACM Version**: 2.14.1
**Clusters**: prod, test
