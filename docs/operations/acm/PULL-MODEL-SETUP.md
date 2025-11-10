# ACM Pull Model Setup

**Alternative to Push Model**: Each managed cluster runs its own Argo CD and pulls configuration directly from Git.

## Architecture Comparison

### Push Model (Current - What We Just Configured)

```
Hub Cluster (Argo CD)
  └─ ApplicationSet
      ├─ Pushes to → Test Cluster
      └─ Pushes to → Prod Cluster
```

**Pros**: Centralized control, single Argo CD instance, easier RBAC
**Cons**: Hub cluster failure affects all deployments, network latency, hub must have access to all clusters

### Pull Model (This Document)

```
Hub Cluster (ACM only)
  └─ Manages cluster inventory

Test Cluster (Argo CD)
  └─ Pulls from Git → Deploys to self

Prod Cluster (Argo CD)
  └─ Pulls from Git → Deploys to self
```

**Pros**: Autonomous clusters, continues working if hub fails, no cross-cluster network requirements
**Cons**: Multiple Argo CD instances to manage, more complex RBAC, need ACM Policies for coordination

## Pull Model Setup

### Prerequisites

- ACM installed on hub cluster
- Managed clusters imported into ACM
- OpenShift GitOps operator installed **on each managed cluster**

### Step 1: Install GitOps on Each Cluster

**From Hub Cluster:**

```bash
# Create Policy to install GitOps operator on all homelab clusters
cat <<POLICY | oc apply -f -
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  name: install-openshift-gitops
  namespace: open-cluster-management-policies
spec:
  disabled: false
  remediationAction: enforce
  policy-templates:
    - objectDefinition:
        apiVersion: policy.open-cluster-management.io/v1
        kind: ConfigurationPolicy
        metadata:
          name: install-gitops-operator
        spec:
          remediationAction: enforce
          severity: high
          object-templates:
            - complianceType: musthave
              objectDefinition:
                apiVersion: operators.coreos.com/v1alpha1
                kind: Subscription
                metadata:
                  name: openshift-gitops-operator
                  namespace: openshift-operators
                spec:
                  channel: latest
                  name: openshift-gitops-operator
                  source: redhat-operators
                  sourceNamespace: openshift-marketplace
                  installPlanApproval: Automatic
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: install-openshift-gitops-binding
  namespace: open-cluster-management-policies
placementRef:
  name: homelab-clusters
  apiGroup: cluster.open-cluster-management.io
  kind: PlacementRule
subjectRef:
  name: install-openshift-gitops
  apiGroup: policy.open-cluster-management.io
  kind: Policy
---
apiVersion: apps.open-cluster-management.io/v1
kind: PlacementRule
metadata:
  name: homelab-clusters
  namespace: open-cluster-management-policies
spec:
  clusterSelector:
    matchExpressions:
      - key: cluster.open-cluster-management.io/clusterset
        operator: In
        values:
          - homelab
POLICY
```

### Step 2: Create Bootstrap Application on Each Cluster

**Option A: Via ACM Policy (Recommended)**

```bash
cat <<POLICY | oc apply -f -
apiVersion: policy.open-cluster-management.io/v1
kind: Policy
metadata:
  name: bootstrap-cluster-application
  namespace: open-cluster-management-policies
spec:
  disabled: false
  remediationAction: enforce
  policy-templates:
    - objectDefinition:
        apiVersion: policy.open-cluster-management.io/v1
        kind: ConfigurationPolicy
        metadata:
          name: create-bootstrap-application
        spec:
          remediationAction: enforce
          severity: high
          object-templates:
            - complianceType: musthave
              objectDefinition:
                apiVersion: argoproj.io/v1alpha1
                kind: Application
                metadata:
                  name: cluster
                  namespace: openshift-gitops
                  finalizers:
                    - resources-finalizer.argocd.argoproj.io
                spec:
                  project: default
                  source:
                    repoURL: https://github.com/rbales79/argo-apps.git
                    targetRevision: framework-dev
                    path: 'roles/{{hub fromClusterClaim "topology" hub}}'
                    helm:
                      valueFiles:
                        - '../../values-{{hub fromClusterClaim "name" hub}}.yaml'
                  destination:
                    server: https://kubernetes.default.svc
                    namespace: openshift-gitops
                  syncPolicy:
                    automated:
                      prune: true
                      selfHeal: true
                    syncOptions:
                      - CreateNamespace=true
---
apiVersion: policy.open-cluster-management.io/v1
kind: PlacementBinding
metadata:
  name: bootstrap-cluster-application-binding
  namespace: open-cluster-management-policies
placementRef:
  name: homelab-clusters
  apiGroup: cluster.open-cluster-management.io
  kind: PlacementRule
subjectRef:
  name: bootstrap-cluster-application
  apiGroup: policy.open-cluster-management.io
  kind: Policy
POLICY
```

**Option B: Manually on Each Cluster**

```bash
# Switch to managed cluster
test  # or prod

# Create bootstrap Application
cat <<EOF | oc apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster
  namespace: openshift-gitops
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/rbales79/argo-apps.git
    targetRevision: framework-dev
    path: roles/sno  # or roles/compact, roles/full
    helm:
      valueFiles:
        - ../../clusters/individual-clusters/values-test.yaml  # or values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: openshift-gitops
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```
