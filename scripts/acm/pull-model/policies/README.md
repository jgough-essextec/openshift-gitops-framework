# ACM Policies for Pull Model

ACM Policies to configure managed clusters for pull-based GitOps deployment.

## Overview

These policies automatically configure each managed cluster to:

1. Install OpenShift GitOps operator
2. Create bootstrap Application that pulls from Git
3. Configure RBAC for Argo CD

## Policies

### 1. Install OpenShift GitOps (`01-install-gitops-policy.yaml`)

**Purpose**: Installs OpenShift GitOps operator on all homelab clusters

**What it does**:

- Creates Subscription for openshift-gitops-operator
- Uses `latest` channel for automatic updates
- InstallPlanApproval: Automatic

**Target**: All clusters in homelab clusterset

**Status Check**:

```bash
# From hub cluster
oc get policy install-openshift-gitops -n open-cluster-management-policies

# On managed cluster
oc get subscription openshift-gitops-operator -n openshift-operators
```

### 2. Bootstrap Application (`02-bootstrap-application-policy.yaml`)

**Purpose**: Creates the "cluster" bootstrap Application on each managed cluster

**What it does**:

- Creates Application pointing to this Git repository
- Uses ACM ClusterClaims to dynamically select:
  - Role path: `roles/{{topology}}` (sno, compact, full)
  - Values file: `values-{{name}}.yaml` (test, prod, hub)
- Enables automated sync with prune and self-heal
- Configures retry logic for transient failures

**Target**: All clusters in homelab clusterset

**Status Check**:

```bash
# From hub cluster
oc get policy bootstrap-cluster-application -n open-cluster-management-policies

# On managed cluster
oc get application cluster -n openshift-gitops
```

### 3. Configure Argo RBAC (`03-configure-argo-rbac-policy.yaml`)

**Purpose**: Grants Argo CD permissions to deploy cluster-scoped resources

**What it does**:

- Creates ClusterRoleBinding for openshift-gitops-argocd-application-controller
- Grants cluster-admin role
- Required for operators, CRDs, ClusterRoles, etc.

**Target**: All clusters in homelab clusterset

**Status Check**:

```bash
# From hub cluster
oc get policy configure-argocd-rbac -n open-cluster-management-policies

# On managed cluster
oc get clusterrolebinding openshift-gitops-argocd-application-controller-cluster-admin
```

## Deployment

### Deploy All Policies

```bash
# From hub cluster
oc create namespace open-cluster-management-policies 2>/dev/null || true
oc apply -f acm/policies/
```

### Verify Deployment

```bash
# Check policies created
oc get policy -n open-cluster-management-policies

# Check compliance status
oc get policy -n open-cluster-management-policies -o wide

# View detailed status
oc describe policy install-openshift-gitops -n open-cluster-management-policies
```

### Monitor Enforcement

```bash
# Watch policy compliance
watch -n 10 'oc get policy -n open-cluster-management-policies -o wide'

# Check on managed clusters
test  # Switch to test cluster
oc get subscription openshift-gitops-operator -n openshift-operators
oc get application cluster -n openshift-gitops
oc get clusterrolebinding openshift-gitops-argocd-application-controller-cluster-admin
```

## ACM ClusterClaims

Policies use ACM ClusterClaims to dynamically configure each cluster:

| ClusterClaim                           | Example Value      | Used For                     |
| -------------------------------------- | ------------------ | ---------------------------- |
| `name`                                 | test, prod, hub    | Selecting values-<name>.yaml |
| `topology`                             | sno, compact, full | Selecting roles/<topology>/  |
| `environment`                          | homelab, cloud     | Conditional logic            |
| `platform.open-cluster-management.io/` | 4.20.2             | Version-specific config      |

### View ClusterClaims

```bash
# From hub cluster
oc get managedcluster test -o jsonpath='{.status.clusterClaims}'

# On managed cluster
oc get clusterclaim
```

### Set Custom ClusterClaims

```bash
# On managed cluster
oc create -f - <<EOF
apiVersion: cluster.open-cluster-management.io/v1alpha1
kind: ClusterClaim
metadata:
  name: topology
spec:
  value: sno
EOF
```

## Troubleshooting

### Policy Not Compliant

```bash
# Check policy details
oc describe policy <policy-name> -n open-cluster-management-policies

# Check PlacementRule
oc get placementrule homelab-clusters -n open-cluster-management-policies -o yaml

# Verify cluster labels
oc get managedcluster -l cluster.open-cluster-management.io/clusterset=homelab
```

### Application Not Created

```bash
# Check policy template status
oc get configurationpolicy -n <cluster-name>

# View policy agent logs (on managed cluster)
oc logs -n open-cluster-management-agent deployment/config-policy-controller
```

### Wrong Values File Used

```bash
# Check ClusterClaim
oc get clusterclaim name -o jsonpath='{.spec.value}'

# Should match your cluster name (test, prod, hub)
# If wrong, update ClusterClaim:
oc patch clusterclaim name --type=merge -p '{"spec":{"value":"test"}}'
```

### GitOps Not Installing

```bash
# Check Subscription status
oc get subscription openshift-gitops-operator -n openshift-operators -o yaml

# Check InstallPlan
oc get installplan -n openshift-operators

# Check CatalogSource
oc get catalogsource redhat-operators -n openshift-marketplace
```

## Policy Customization

### Change Target Clusters

Edit PlacementRule to target different clusters:

```yaml
# Target only production clusters
spec:
  clusterSelector:
    matchExpressions:
      - key: environment
        operator: In
        values:
          - production
```

```yaml
# Target only SNO topology
spec:
  clusterSelector:
    matchExpressions:
      - key: topology
        operator: In
        values:
          - sno
```

### Change Git Repository

Edit bootstrap application policy to use different repo:

```yaml
source:
  repoURL: https://github.com/your-org/your-repo.git
  targetRevision: main
```

### Change Enforcement

Set `remediationAction: inform` to only report, not enforce:

```yaml
spec:
  remediationAction: inform # Change from enforce
```

## Compliance Monitoring

### View Compliance Dashboard

```bash
# ACM Console > Governance > Policies
# Or via CLI:
oc get policy -n open-cluster-management-policies -o wide
```

### Export Compliance Report

```bash
oc get policy -n open-cluster-management-policies -o json > policy-compliance-report.json
```

## Cleanup

### Remove Policies

```bash
oc delete -f acm/policies/
```

### Remove PlacementRule

```bash
oc delete placementrule homelab-clusters -n open-cluster-management-policies
```

### Remove Namespace

```bash
oc delete namespace open-cluster-management-policies
```

## Best Practices

1. **Start with inform mode** - Test policies before enforcing
2. **Use PlacementRules effectively** - Target specific cluster groups
3. **Monitor compliance** - Check policy status regularly
4. **Version control policies** - Keep in Git alongside apps
5. **Document exceptions** - If clusters need different config
6. **Test on test cluster first** - Before rolling to prod
7. **Use ClusterClaims** - For dynamic configuration

## Next Steps

1. Deploy policies to hub cluster
2. Verify compliance on test cluster
3. Validate bootstrap Application created
4. Check ApplicationSets deploying
5. Monitor application health
6. Roll out to production clusters

## References

- [ACM Policy Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/2.14/html/governance/index)
- [Policy Examples](https://github.com/stolostron/policy-collection)
- [ClusterClaims Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/2.14/html/clusters/managing-your-clusters#clusterclaims)

---

**Model**: Pull (Cluster-managed)
**Automation**: ACM Policies
**Status**: Ready for deployment
