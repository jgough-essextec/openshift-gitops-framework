# Getting Started with ACM (Advanced Cluster Management)

> **📋 Strategic Context:** See [ADR 008: Multi-Cluster Management Strategy](./decisions/008-multi-cluster-management-strategy.md) for the architectural decision and rationale behind using ACM.

This guide explains how to use Red Hat Advanced Cluster Management (ACM) with this GitOps repository.

## What is ACM?

**Advanced Cluster Management for Kubernetes (ACM)** is Red Hat's solution for managing multiple OpenShift/Kubernetes clusters from a single control plane. It provides:

- **Multi-cluster Management**: Deploy and manage multiple clusters from a hub cluster
- **Application Lifecycle**: Deploy applications across multiple clusters using GitOps
- **Governance & Policy**: Enforce security policies and compliance across clusters
- **Observability**: Monitor cluster health and application performance
- **Cluster Provisioning**: Automated cluster deployment on multiple cloud providers

## Architecture

This repository deploys ACM in a **hub-and-spoke** model:

```
Hub Cluster (ACM Control Plane)
    ↓
Managed Clusters (Spoke Clusters)
    - Prod (SNO topology)
    - Test Cluster
    - Other clusters
```

**Note**: SNO (Single Node OpenShift) is a topology type, not a cluster name. The production cluster uses SNO topology.

### Components

ACM automatically deploys these components:

1. **ACM Operator** - Core management platform
2. **Multicluster Engine (MCE)** - Cluster lifecycle management
3. **Application Lifecycle** - GitOps application deployment
4. **Governance** - Policy engine for compliance
5. **Observability** - Cluster and application monitoring (optional)

## Prerequisites

- **Hub Cluster**: Compact (3-node) or Full (6+ node) OpenShift cluster
  - SNO topology (Single Node) is NOT supported for ACM hub
- **Resources**:
  - **High Availability**: 16 vCPU, 32GB RAM minimum
  - **Basic Availability** (home lab): 8 vCPU, 16GB RAM minimum
- **Managed Clusters**: Any OpenShift 4.12+ or Kubernetes 1.25+ cluster
- **Network Access**: Hub must be able to reach managed clusters

## Configuration

### Availability Modes

ACM supports two availability configurations:

| Mode      | Use Case              | Replicas          | Resources         | Recommended For             |
| --------- | --------------------- | ----------------- | ----------------- | --------------------------- |
| **Basic** | Development, Home Lab | 1-2 per component | 8 vCPU, 16GB RAM  | Testing, small deployments  |
| **High**  | Production            | 2-3 per component | 16 vCPU, 32GB RAM | Production, HA requirements |

### Enabling ACM on Hub Cluster

ACM is configured in `values-hub.yaml`:

```yaml
clusterGroup:
  platformComponents:
    acm:
      enabled: true # Enable ACM
      version: "2.14.1"
      availabilityConfig: Basic # or High for production
    multiclusterEngine:
      enabled: false # MCE is automatically deployed by ACM
```

**Important**: Do NOT enable `multiclusterEngine` separately - ACM deploys MCE automatically.

### Configuration Hierarchy

Configuration follows the standard values hierarchy:

```
values-global.yaml (pattern defaults)
  ↓
values-home.yaml (cluster set - defines Basic availability for home lab)
  ↓
values-hub.yaml (specific cluster - enables ACM)
```

Example in `values-home.yaml`:

```yaml
# Home lab defaults - minimal resources even on compact topology
platformComponents:
  acm:
    availabilityConfig: Basic # Override chart default of High
  multiclusterEngine:
    availabilityConfig: Basic # Applied when ACM creates MCE

topology:
  replicas:
    default: 1 # Minimal replicas for home lab
  pdb:
    enabled: false # Disable PDBs for minimal overhead
```

## Deployment

### 1. Verify Prerequisites

```bash
# Switch to hub cluster
hub

# Verify node count (3+ nodes required)
oc get nodes

# Verify resources available
oc describe nodes | grep -A 5 "Allocated resources"
```

### 2. Enable ACM in Configuration

Edit `values-hub.yaml`:

```yaml
platformComponents:
  acm:
    enabled: true
    availabilityConfig: Basic # or High
```

Commit and push:

```bash
git add values-hub.yaml
git commit -m "Enable ACM on hub cluster"
git push
```

### 3. Monitor Deployment

```bash
# Watch Argo CD sync ACM Application
oc get application.argoproj.io advanced-cluster-management -n openshift-gitops -w

# Check ACM operator installation
oc get csv -n open-cluster-management | grep advanced-cluster

# Watch MultiClusterHub deployment
oc get multiclusterhub -n open-cluster-management -w

# Check MCE deployment (created by ACM)
oc get multiclusterengine -A
oc get pods -n multicluster-engine

# Check all ACM pods
oc get pods -n open-cluster-management
```

### 4. Deployment Timeline

- **ACM Operator**: 2-3 minutes
- **MCE Deployment**: 5-7 minutes
- **ACM Components**: 10-15 minutes
- **Total Time**: ~20 minutes (Basic) / ~30 minutes (High)

### 5. Access ACM Console

```bash
# Get the ACM console route
oc get route multicloud-console -n open-cluster-management

# Access using OpenShift console integration
# Navigate to: All Clusters → Infrastructure → Clusters
```

## Managing Clusters

### Import an Existing Cluster

1. **Via ACM Console**:

   - Navigate to: Infrastructure → Clusters
   - Click "Import cluster"
   - Name the cluster (e.g., "prod", "test")
   - Download or copy the import command
   - Run the command on the managed cluster

2. **Via CLI**:

```bash
# On hub cluster, create ManagedCluster resource
cat <<EOF | oc apply -f -
apiVersion: cluster.open-cluster-management.io/v1
kind: ManagedCluster
metadata:
  name: prod  # Cluster name
  labels:
    cloud: BareMetal
    vendor: OpenShift
    environment: production
    topology: sno  # SNO is a topology, not a cluster name
spec:
  hubAcceptsClient: true
EOF

# Get import command
oc get secret prod-import -n prod -o jsonpath='{.data.import\.yaml}' | base64 -d > import-prod.yaml

# On managed cluster, apply import
oc apply -f import-prod.yaml
```

### Verify Cluster Import

```bash
# On hub cluster
oc get managedclusters

# Check cluster status
oc get managedcluster prod -o yaml | grep -A 10 "conditions:"

# View in console
# Navigate to: Infrastructure → Clusters → prod
```

### Organize Clusters with ClusterSets

ClusterSets group clusters for RBAC and application targeting:

```yaml
apiVersion: cluster.open-cluster-management.io/v1beta2
kind: ManagedClusterSet
metadata:
  name: home-lab
spec:
  clusterSelector:
    selectorType: LabelSelector
    labelSelector:
      matchLabels:
        environment: homelab
```

```bash
# Apply clusterset
oc apply -f clusterset.yaml

# Assign clusters to clusterset (add label)
oc label managedcluster prod cluster.open-cluster-management.io/clusterset=home-lab
oc label managedcluster test cluster.open-cluster-management.io/clusterset=home-lab
```

## Deploying Applications with ACM

### Method 1: ApplicationSet (Recommended for this repo)

This repository uses Argo CD ApplicationSets. ACM can manage ApplicationSet placement across clusters.

Create a Placement to target clusters:

```yaml
apiVersion: cluster.open-cluster-management.io/v1beta1
kind: Placement
metadata:
  name: home-lab-placement
  namespace: openshift-gitops
spec:
  predicates:
    - requiredClusterSelector:
        labelSelector:
          matchExpressions:
            - key: environment
              operator: In
              values:
                - homelab
```

### Method 2: ACM Application

ACM can deploy Helm charts or Git repos directly:

```yaml
apiVersion: app.k8s.io/v1beta1
kind: Application
metadata:
  name: ollama
  namespace: openshift-gitops
spec:
  componentKinds:
    - group: apps.open-cluster-management.io
      kind: Subscription
  selector:
    matchExpressions:
      - key: app
        operator: In
        values:
          - ollama
---
apiVersion: apps.open-cluster-management.io/v1
kind: Channel
metadata:
  name: argo-apps-git
  namespace: openshift-gitops
spec:
  type: Git
  pathname: https://github.com/rbales79/argo-apps
---
apiVersion: apps.open-cluster-management.io/v1
kind: Subscription
metadata:
  name: ollama-subscription
  namespace: openshift-gitops
  labels:
    app: ollama
spec:
  channel: openshift-gitops/argo-apps-git
  placement:
    placementRef:
      name: home-lab-placement
      kind: Placement
  packageOverrides:
    - packageName: ollama
      packageAlias: ollama
```

### Method 3: GitOpsCluster (Integrate with Argo CD)

Link ACM-managed clusters to Argo CD:

```yaml
apiVersion: apps.open-cluster-management.io/v1beta1
kind: GitOpsCluster
metadata:
  name: prod
  namespace: openshift-gitops
spec:
  argoServer:
    cluster: local-cluster
    argoNamespace: openshift-gitops
  placementRef:
    kind: Placement
    apiVersion: cluster.open-cluster-management.io/v1beta1
    name: prod-placement
```

## Governance and Policies

### Example: Ensure namespace exists on all clusters

```yaml
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  name: policy-namespace
  namespace: openshift-gitops
spec:
  remediationAction: enforce # or inform
  disabled: false
  policy-templates:
    - objectDefinition:
        apiVersion: policy.open-cluster-management.io/v1
        kind: ConfigurationPolicy
        metadata:
          name: policy-namespace
        spec:
          remediationAction: enforce
          severity: low
          object-templates:
            - complianceType: musthave
              objectDefinition:
                apiVersion: v1
                kind: Namespace
                metadata:
                  name: ollama
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: binding-policy-namespace
  namespace: openshift-gitops
placementRef:
  name: home-lab-placement
  kind: Placement
  apiGroup: cluster.open-cluster-management.io
subjects:
  - name: policy-namespace
    kind: Policy
    apiGroup: policy.open-cluster-management.io
```

Apply policy:

```bash
oc apply -f policy-namespace.yaml

# Check policy status
oc get policy -n openshift-gitops
oc get policy policy-namespace -n openshift-gitops -o yaml
```

## Troubleshooting

### ACM Operator Issues

```bash
# Check operator logs
oc logs -n open-cluster-management -l name=multiclusterhub-operator --tail=50

# Check MultiClusterHub status
oc get multiclusterhub multiclusterhub -n open-cluster-management -o yaml

# Check component status
oc get multiclusterhub multiclusterhub -n open-cluster-management -o jsonpath='{.status.components}' | jq

# Check for failed pods
oc get pods -n open-cluster-management | grep -vE "Running|Completed"
```

### MCE Issues

```bash
# Check MCE operator logs
oc logs -n multicluster-engine -l control-plane=backplane-operator --tail=50

# Check MultiClusterEngine status
oc get multiclusterengine -o yaml

# Check MCE pods
oc get pods -n multicluster-engine
```

### Cluster Import Issues

```bash
# On hub cluster, check ManagedCluster status
oc get managedcluster <cluster-name> -o yaml

# Check klusterlet operator on managed cluster
oc get pods -n open-cluster-management-agent
oc get pods -n open-cluster-management-agent-addon

# Check klusterlet logs
oc logs -n open-cluster-management-agent -l app=klusterlet
```

### Common Issues

#### 1. **Stuck in "Installing" Phase**

**Symptom**: MultiClusterHub stuck installing for >30 minutes

**Solution**:

```bash
# Check if MCE is ready
oc get multiclusterengine -o yaml | grep -A 5 "conditions:"

# If MCE is stuck, check operator logs
oc logs -n multicluster-engine -l control-plane=backplane-operator --tail=100
```

#### 2. **Validating Webhook Errors**

**Symptom**: Cannot delete MultiClusterHub - webhook errors

**Solution**:

```bash
# Delete stale webhooks
oc delete validatingwebhookconfiguration multiclusterhub-operator-validating-webhook
oc delete validatingwebhookconfiguration multiclusterengines.multicluster.openshift.io

# Try deletion again
oc delete multiclusterhub multiclusterhub -n open-cluster-management
```

#### 3. **Insufficient Resources**

**Symptom**: Pods pending or OOMKilled

**Solution**:

- Use Basic availability mode for resource-constrained environments
- Ensure nodes meet minimum requirements (3 nodes, 8 vCPU, 16GB RAM)
- Disable observability if not needed

#### 4. **ManagedCluster Stuck Deleting**

**Symptom**: ManagedCluster has deletionTimestamp but won't delete

**Solution**:

```bash
# Remove finalizers
oc patch managedcluster <name> -p '{"metadata":{"finalizers":[]}}' --type=merge
```

## Cleanup and Removal

### Uninstall ACM

**Warning**: This will remove all ACM components and detach managed clusters.

```bash
# 1. Detach all managed clusters first
oc delete managedclusters --all

# 2. Delete MultiClusterHub
oc delete multiclusterhub multiclusterhub -n open-cluster-management

# 3. Wait for cleanup (5-10 minutes)
watch oc get pods -n open-cluster-management

# 4. Disable in values-hub.yaml
# Set acm.enabled: false

# 5. Let Argo CD clean up
oc delete application.argoproj.io advanced-cluster-management -n openshift-gitops
```

### Remove ACM from Managed Cluster

```bash
# On managed cluster
oc delete namespace open-cluster-management-agent
oc delete namespace open-cluster-management-agent-addon
oc delete klusterlet klusterlet
```

## Best Practices

### 1. **Use ClusterSets for Organization**

Group clusters by environment, location, or purpose:

```yaml
ClusterSets:
  - home-lab (dev/test)
  - production
  - edge-sites
```

### 2. **Label Clusters Appropriately**

Use consistent labels for Placement targeting:

```yaml
labels:
  environment: production
  cloud: BareMetal
  region: us-east
  topology: sno # SNO = Single Node OpenShift topology
  clusterSet: home-lab
```

### 3. **Start with Basic Availability**

Use Basic mode for testing, then upgrade to High for production:

```yaml
# Test with Basic
availabilityConfig: Basic

# Upgrade to High when ready
availabilityConfig: High
```

### 4. **Monitor Resource Usage**

```bash
# Check resource consumption
oc adm top pods -n open-cluster-management
oc adm top pods -n multicluster-engine

# Use VPA recommendations (enabled in this repo)
oc get vpa -n open-cluster-management
```

### 5. **Use Policies for Compliance**

Create policies for:

- Required namespaces
- Required operators
- Security constraints
- Resource quotas
- Network policies

### 6. **Backup ACM Configuration**

```bash
# Backup important resources
oc get multiclusterhub -n open-cluster-management -o yaml > acm-backup.yaml
oc get managedclusters -o yaml > managedclusters-backup.yaml
oc get policies -A -o yaml > policies-backup.yaml
```

## Reference

### ACM Components in This Repository

- **Chart Location**: `charts/platform/advanced-cluster-management/`
- **Templates**:
  - `operator.yaml` - ACM operator subscription
  - `multiclusterhub.yaml` - ACM instance configuration
- **Values**:
  - Chart defaults: `charts/platform/advanced-cluster-management/values.yaml`
  - Cluster-specific: `values-hub.yaml`
  - Cluster-set defaults: `values-home.yaml`

### MCE Components

- **Chart Location**: `charts/platform/multicluster-engine/`
- **Note**: MCE is automatically deployed by ACM - do not enable separately
- **Configuration**: MCE inherits availabilityConfig from ACM

### Useful Commands

```bash
# Hub cluster status
oc get multiclusterhub,multiclusterengine --all-namespaces

# All managed clusters
oc get managedclusters

# Cluster details
oc describe managedcluster <name>

# Application status across clusters
oc get applications -A

# Policy compliance
oc get policy -A

# ACM console URL
oc get route multicloud-console -n open-cluster-management -o jsonpath='{.spec.host}'
```

### Documentation Links

- [ACM Official Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes)
- [MCE Documentation](https://access.redhat.com/documentation/en-us/multicluster_engine_for_kubernetes)
- [ACM GitHub](https://github.com/stolostron)
- [Red Hat Validated Patterns](https://validatedpatterns.io/)

## Support

- **Issues**: File GitHub issue with `[ACM]` prefix
- **Questions**: GitHub Discussions
- **Community**: OpenShift Community Slack #advanced-cluster-management

---

## Next Steps

1. ✅ Deploy ACM on hub cluster
2. ✅ Verify ACM console access
3. 🔲 Import managed clusters (Prod, Test)
4. 🔲 Create ClusterSets and Placements
5. 🔲 Deploy applications across clusters
6. 🔲 Set up governance policies
7. 🔲 Configure observability (optional)
