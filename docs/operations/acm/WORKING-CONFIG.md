# ACM Platform Deployment - Working Configuration

## Summary

Successfully deployed platform components to managed clusters using ACM and Argo CD integration.

## Architecture

```
Hub Cluster (hub.roybales.com)
  └─ ACM (Advanced Cluster Management)
      ├─ ManagedClusterSet: homelab
      │   └─ ManagedCluster: test
      ├─ Placement: platform-placement-1
      │   └─ PlacementDecision: selects test cluster
      ├─ GitOpsCluster: homelab-gitops
      │   └─ Creates cluster secret in openshift-gitops
      └─ Argo CD ApplicationSet: homelab-platform-simple
          └─ Generates 8 Applications for test cluster

Test Cluster (test.roybales.com)
  └─ Platform Components (deployed via ACM)
      ├─ external-secrets-operator
      ├─ certificates  
      ├─ openshift-nfd
      ├─ vertical-pod-autoscaler
      ├─ goldilocks
      ├─ gatus
      ├─ generic-device-plugin
      └─ snapshot-finalizer-remover
```

## Key Components

### 1. GitOpsCluster Resource

The breakthrough was creating a `GitOpsCluster` resource that bridges ACM and Argo CD:

```yaml
apiVersion: apps.open-cluster-management.io/v1beta1
kind: GitOpsCluster
metadata:
  name: homelab-gitops
  namespace: openshift-gitops
spec:
  argoServer:
    cluster: local-cluster
    argoNamespace: openshift-gitops
  placementRef:
    kind: Placement
    apiVersion: cluster.open-cluster-management.io/v1beta1
    name: platform-placement-1
    namespace: openshift-gitops
```

This automatically:
- Creates Argo CD cluster secrets for managed clusters
- Syncs cluster metadata as labels
- Enables Argo CD to deploy to ACM-managed clusters

### 2. ApplicationSet with Clusters Generator

Using the `clusters` generator instead of `clusterDecisionResource` avoids RBAC complications:

```yaml
generators:
  - matrix:
      generators:
        - clusters:
            selector:
              matchLabels:
                vendor: OpenShift
              matchExpressions:
                - key: name
                  operator: NotIn
                  values: [in-cluster, local-cluster]
        - list:
            elements:
              - component: external-secrets-operator
                syncWave: "0"
                createNamespace: "true"
```

### 3. Cluster Secret Labels

ACM automatically adds labels to cluster secrets:

```yaml
labels:
  apps.open-cluster-management.io/acm-cluster: "true"
  apps.open-cluster-management.io/cluster-name: test
  apps.open-cluster-management.io/cluster-server: api.test.roybales.com
  cloud: Other
  cluster.open-cluster-management.io/clusterset: homelab
  environment: homelab
  name: test
  openshiftVersion: 4.20.2
  topology: sno
  vendor: OpenShift
```

These labels enable selective deployment via ApplicationSet selectors.

## Deployment Process

1. **Create ManagedClusterSet**:
   ```bash
   oc apply -f acm/01-managedclusterset.yaml
   ```

2. **Create ManagedClusterSetBinding**:
   ```bash
   oc apply -f acm/02-managedclustersetbinding.yaml
   ```

3. **Create Placement**:
   ```bash
   oc apply -f acm/03-placement-platform.yaml
   ```

4. **Label clusters**:
   ```bash
   oc label managedcluster test cluster.open-cluster-management.io/clusterset=homelab
   ```

5. **Create GitOpsCluster**:
   ```bash
   cat <<EOF | oc apply -f -
   apiVersion: apps.open-cluster-management.io/v1beta1
   kind: GitOpsCluster
   metadata:
     name: homelab-gitops
     namespace: openshift-gitops
   spec:
     argoServer:
       cluster: local-cluster
       argoNamespace: openshift-gitops
     placementRef:
       kind: Placement
       apiVersion: cluster.open-cluster-management.io/v1beta1
       name: platform-placement-1
       namespace: openshift-gitops
   EOF
   ```

6. **Deploy ApplicationSet**:
   ```bash
   oc apply -f acm/homelab-platform-simple.yaml
   ```

## Verification

### Check GitOpsCluster

```bash
oc get gitopscluster -n openshift-gitops
```

### Check Cluster Secrets

```bash
oc get secrets -n openshift-gitops -l argocd.argoproj.io/secret-type=cluster
```

### Check Generated Applications

```bash
oc get applications.argoproj.io -n openshift-gitops | grep test-
```

### Check Application Status on Test Cluster

Switch to test cluster and verify:

```bash
test
oc get pods -n external-secrets-operator
oc get pods -n openshift-nfd
oc get pods -n goldilocks
```

## Lessons Learned

1. **GitOpsCluster is Essential**: The `GitOpsCluster` resource is the missing link between ACM and Argo CD. Without it, cluster secrets aren't created.

2. **Clusters Generator vs ClusterDecisionResource**: The `clusters` generator is simpler and avoids RBAC issues with PlacementDecisions.

3. **Matrix Generator Key Conflicts**: When using matrix generators, be careful about key name conflicts between generators (e.g., both generators providing `name`).

4. **ACM Labels are Powerful**: ACM automatically enriches cluster secrets with useful labels that can be used for selective deployment.

5. **Start Small**: Begin with one cluster (test) before adding production clusters.

## Troubleshooting

### Applications Not Generated

- Check GitOpsCluster exists: `oc get gitopscluster -n openshift-gitops`
- Check cluster secrets: `oc get secrets -n openshift-gitops -l argocd.argoproj.io/secret-type=cluster`
- Check ApplicationSet status: `oc describe applicationset homelab-platform-simple -n openshift-gitops`

### Applications Stuck OutOfSync

- Check application details: `oc describe application.argoproj.io test-<component> -n openshift-gitops`
- Check target cluster connectivity: Switch to cluster and verify access
- Check Argo CD sync status in UI: `https://openshift-gitops-server-openshift-gitops.apps.hub.roybales.com`

### Cluster Secret Not Created

- Verify ManagedClusterSet membership: `oc get managedcluster -l cluster.open-cluster-management.io/clusterset=homelab`
- Check Placement decisions: `oc get placementdecision -n openshift-gitops`
- Recreate GitOpsCluster if needed

## Next Steps

1. Monitor test cluster deployments until all healthy
2. Add prod cluster to homelab clusterset
3. Verify deployment to both clusters
4. Document any cluster-specific configuration needs
5. Consider adding more selective placement rules (e.g., by environment or topology)

## Files

- **Working ApplicationSet**: `acm/homelab-platform-simple.yaml`
- **GitOpsCluster**: Created via command (should be added to repo)
- **Core ACM Config**: `acm/01-*.yaml`, `acm/02-*.yaml`, `acm/03-*.yaml`

---

**Status**: ✅ Working as of November 7, 2025
**Deployed Components**: 8 platform components
**Target Cluster**: test.roybales.com
**Hub Cluster**: hub.roybales.com
