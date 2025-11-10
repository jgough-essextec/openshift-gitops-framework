# ACM Platform Deployment Status

**Date**: November 7, 2025  
**Hub Cluster**: hub.roybales.com  
**Target Clusters**: test.roybales.com  
**Status**: ✅ **DEPLOYED AND SYNCING**

## Deployed Components

The following platform components are being deployed to the test cluster via ACM:

| Component | Sync Status | Health Status | Purpose |
|-----------|-------------|---------------|---------|
| external-secrets-operator | OutOfSync | Degraded | Secrets management via external providers |
| certificates | OutOfSync | Degraded | Certificate management and issuance |
| openshift-nfd | OutOfSync | Progressing | Node Feature Discovery for hardware detection |
| vertical-pod-autoscaler | OutOfSync | Progressing | Automatic pod resource optimization |
| goldilocks | Synced | Degraded | VPA recommendations dashboard |
| gatus | Synced | Progressing | Health monitoring and status page |
| generic-device-plugin | OutOfSync | Healthy | Custom device plugin framework |
| snapshot-finalizer-remover | Synced | Healthy | Volume snapshot cleanup automation |

**Note**: `OutOfSync` and `Degraded` statuses are normal during initial deployment as operators install and reconcile.

## Configuration Files

### Core ACM Resources (Apply in Order)

1. `01-managedclusterset.yaml` - Defines the homelab cluster set
2. `02-managedclustersetbinding.yaml` - Binds cluster set to openshift-gitops namespace
3. `03-placement-platform.yaml` - Placement rule for selecting clusters
4. `04-label-clusters.sh` - Script to label managed clusters
5. `05-gitopscluster.yaml` - **NEW** - ACM-Argo CD integration bridge

### ApplicationSet

- `homelab-platform-simple.yaml` - Working ApplicationSet using clusters generator

### Deployment Scripts

- `deploy-acm-config.sh` - Automated deployment
- `cleanup-acm-config.sh` - Cleanup script

## Quick Commands

### Check Deployment Status

```bash
# On hub cluster
oc get applications.argoproj.io -n openshift-gitops | grep test-

# Check cluster secrets
oc get secrets -n openshift-gitops -l argocd.argoproj.io/secret-type=cluster

# Check GitOpsCluster
oc get gitopscluster -n openshift-gitops
```

### Switch to Test Cluster and Verify

```bash
test
oc get pods -n external-secrets-operator
oc get pods -n openshift-nfd  
oc get pods -n goldilocks
oc get subscription -n openshift-operators
```

### Monitor Sync Progress

```bash
# Watch applications sync
watch -n 5 'oc get applications.argoproj.io -n openshift-gitops | grep test-'

# Check specific application
oc describe application.argoproj.io test-external-secrets-operator -n openshift-gitops
```

## Adding More Clusters

To add prod cluster to ACM management:

```bash
# Label prod cluster
oc label managedcluster prod cluster.open-cluster-management.io/clusterset=homelab

# Verify placement
oc get placementdecision platform-placement-1-decision-1 -n openshift-gitops -o jsonpath='{.status.decisions[*].clusterName}'

# Applications will automatically generate for prod
oc get applications.argoproj.io -n openshift-gitops | grep prod-
```

## Troubleshooting

### Applications Not Appearing

1. Check GitOpsCluster exists:
   ```bash
   oc get gitopscluster homelab-gitops -n openshift-gitops
   ```

2. Check cluster secrets created:
   ```bash
   oc get secrets -n openshift-gitops -l apps.open-cluster-management.io/acm-cluster=true
   ```

3. Check ApplicationSet status:
   ```bash
   oc describe applicationset homelab-platform-simple -n openshift-gitops
   ```

### Sync Failures

1. Check application events:
   ```bash
   oc describe application.argoproj.io test-<component> -n openshift-gitops
   ```

2. Check Argo CD logs:
   ```bash
   oc logs -n openshift-gitops deployment/openshift-gitops-application-controller
   ```

3. Verify cluster connectivity from hub

## Next Steps

1. ✅ **Monitor current deployments** - Wait for all components to reach Healthy status
2. ⏳ **Add prod cluster** - Once test validates successfully
3. ⏳ **Add storage components** - TrueNAS, custom-error-pages
4. ⏳ **Add application domains** - ai, media, home-automation, etc.

---

**Working Configuration Documented**: See `WORKING-CONFIG.md` for technical details.
