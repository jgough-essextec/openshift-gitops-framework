# ACM Platform Deployment - Quick Start

**⚡ Fast deployment guide for ACM-managed platform components**

## Prerequisites

✅ Hub cluster with ACM installed  
✅ Managed clusters imported into ACM  
✅ OpenShift GitOps operator installed on hub

## 5-Minute Deployment

### 1. Create Core ACM Resources

```bash
cd /workspaces/argo-apps/acm
oc apply -f 01-managedclusterset.yaml
oc apply -f 02-managedclustersetbinding.yaml
oc apply -f 03-placement-platform.yaml
```

### 2. Label Your Clusters

```bash
# For test cluster only (recommended for first deployment)
oc label managedcluster test cluster.open-cluster-management.io/clusterset=homelab

# Or for both clusters
oc label managedcluster test cluster.open-cluster-management.io/clusterset=homelab
oc label managedcluster prod cluster.open-cluster-management.io/clusterset=homelab
```

### 3. Create GitOpsCluster Bridge

```bash
oc apply -f 05-gitopscluster.yaml
```

**Wait 10-15 seconds** for cluster secrets to be created.

### 4. Deploy ApplicationSet

```bash
oc apply -f homelab-platform-simple.yaml
```

### 5. Verify Deployment

```bash
# Check cluster secrets created
oc get secrets -n openshift-gitops -l argocd.argoproj.io/secret-type=cluster

# Check applications generated (use test- or prod- depending on what you labeled)
oc get applications.argoproj.io -n openshift-gitops | grep test-

# Watch sync progress
watch -n 5 'oc get applications.argoproj.io -n openshift-gitops | grep test-'
```

## What Gets Deployed

8 platform components to each managed cluster:

| Component | Purpose |
|-----------|---------|
| external-secrets-operator | Secrets from external sources |
| certificates | Cert management via cert-manager |
| openshift-nfd | Hardware feature discovery |
| vertical-pod-autoscaler | Auto resource tuning |
| goldilocks | VPA recommendations UI |
| gatus | Health monitoring |
| generic-device-plugin | Custom device plugins |
| snapshot-finalizer-remover | Volume snapshot cleanup |

## Verification Commands

```bash
# On hub cluster
oc get gitopscluster -n openshift-gitops
oc get placementdecision -n openshift-gitops
oc get applications.argoproj.io -n openshift-gitops | grep -E "test-|prod-"

# Switch to managed cluster
test  # or: prod
oc get pods -n external-secrets-operator
oc get pods -n openshift-nfd
oc get subscription -n openshift-operators
```

## Troubleshooting

### No Applications Generated

```bash
# Check GitOpsCluster
oc get gitopscluster -n openshift-gitops

# Check cluster secrets  
oc get secrets -n openshift-gitops -l apps.open-cluster-management.io/acm-cluster=true

# Check ApplicationSet status
oc describe applicationset homelab-platform-simple -n openshift-gitops
```

### Applications Stuck OutOfSync

Normal during initial deployment. Wait 5-10 minutes for operators to install.

```bash
# Check specific application
oc describe application.argoproj.io test-external-secrets-operator -n openshift-gitops

# Check Argo CD application controller logs
oc logs -n openshift-gitops deployment/openshift-gitops-application-controller --tail=50
```

### Remove Everything

```bash
oc delete applicationset homelab-platform-simple -n openshift-gitops
oc delete gitopscluster homelab-gitops -n openshift-gitops
oc delete placement platform-placement-1 -n openshift-gitops
oc delete managedclustersetbinding homelab -n openshift-gitops
oc delete managedclusterset homelab
```

## Adding More Clusters

Just label them:

```bash
oc label managedcluster <cluster-name> cluster.open-cluster-management.io/clusterset=homelab
```

Applications will automatically generate within 30 seconds.

## Next Steps

- **Monitor**: Watch applications sync on Argo CD UI
- **Validate**: Switch to managed clusters and verify pods running
- **Expand**: Add more platform components to ApplicationSet
- **Automate**: Add application domains (ai, media, etc.)

## Documentation

- **Technical Details**: `WORKING-CONFIG.md`
- **Full Guide**: `README.md`
- **Current Status**: `DEPLOYMENT-STATUS.md`

---

**🎉 You're done!** Platform components are deploying to your managed clusters via ACM.
