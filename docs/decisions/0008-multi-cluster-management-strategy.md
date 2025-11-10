---
status: "accepted"
date: 2025-11-07
decision-makers:
  - Roy Bales
consulted:
  - Red Hat Advanced Cluster Management Documentation
  - Red Hat Validated Patterns Framework
informed:
  - Operations Team
---

# ADR 008: Multi-Cluster Management Strategy

## Context and Problem Statement

As the infrastructure evolved from a single cluster to multiple clusters across different sites (home lab, work lab, future cloud), we needed a strategy for:

1. **Cluster Lifecycle:** Provisioning, configuration, and decommissioning
2. **GitOps Model:** Pull vs push patterns for application deployment
3. **Central Management:** Hub cluster for policy and observability
4. **Network Topology:** Hub-and-spoke vs mesh vs independent clusters
5. **Scalability:** Support for 2-5 clusters initially, 10+ in future
6. **Credential Management:** Kubeconfig and authentication across clusters

## Decision Drivers

- Small cluster fleet (currently 3, target 5-10)
- Mix of on-premise and potential cloud clusters
- Need for centralized observability and policy management
- GitOps-first approach (everything in Git)
- Minimize operational complexity
- Support disconnected/edge scenarios
- Multi-tenancy not a primary requirement
- Cost-effectiveness (Red Hat subscriptions)

## Considered Options

1. **Independent Clusters** - No centralized management, per-cluster GitOps
2. **Hub-and-Spoke with ACM** - Central hub with Red Hat ACM/MCE (chosen)
3. **Full Mesh** - All clusters peer with each other
4. **External Management Platform** - Rancher, Crossplane, etc.
5. **Cloud-Native Multi-Cluster** - AWS EKS Anywhere, Azure Arc, GKE Enterprise

## Decision Outcome

Chosen option: **Hub-and-Spoke with ACM (Advanced Cluster Management)**, because it provides the best balance of centralized control and operational simplicity for small-to-medium cluster fleets.

### Architecture

```
┌─────────────────────────────────────────────────┐
│ Hub Cluster (Management)                         │
│ - Red Hat ACM (Advanced Cluster Management)      │
│ - MCE (Multicluster Engine)                     │
│ - Central GitOps (OpenShift GitOps/Argo CD)      │
│ - Observability Stack (Prometheus/Grafana)       │
│ - Policy Engine                                  │
└─────────────┬────────────┬──────────────────────┘
              │            │
       ┌──────┴───┐   ┌────┴──────┐
       │          │   │           │
┌──────▼──────┐ ┌▼───▼───────┐ ┌─▼────────────┐
│ SNO Prod    │ │ Test       │ │ Work Lab     │
│ (Managed)   │ │ (Managed)  │ │ (Managed)    │
│             │ │            │ │              │
│ Local GitOps│ │ Local      │ │ Local GitOps │
│ (Pull Model)│ │ GitOps     │ │ (Pull Model) │
└─────────────┘ └────────────┘ └──────────────┘
```

### Hub Cluster Configuration

**Enabled Components:**

- Advanced Cluster Management (ACM)
- Multicluster Engine (MCE)
- OpenShift GitOps (Argo CD)
- Observability (optional)
- Backup/DR coordination (Kasten K10)

**Hub Values Configuration:**

```yaml
# clusters/individual-clusters/values-hub.yaml
clusterGroup:
  name: hub
  role: management

  platformComponents:
    advancedClusterManagement:
      enabled: true
    multiclusterEngine:
      enabled: true
    argocd:
      enabled: true
    gatus:
      enabled: true

  # Applications typically disabled on hub
  applicationStacks:
    ai:
      enabled: false
    media:
      enabled: false
```

### Managed Cluster Configuration

**Pattern:** GitOps Pull Model (Preferred)

Each managed cluster runs its own OpenShift GitOps instance and pulls configuration from Git:

```yaml
# clusters/individual-clusters/values-prod.yaml
clusterGroup:
  name: prod
  role: spoke
  hub:
    enabled: true
    cluster: hub.home.example.com

  platformComponents:
    advancedClusterManagement:
      enabled: false # Only on hub
    multiclusterEngine:
      enabled: false # Only on hub
    argocd:
      enabled: true # Local GitOps

  applicationStacks:
    media:
      enabled: true
      apps:
        - plex
        - sonarr
```

### GitOps Models

#### Pull Model (Default/Preferred)

**How it Works:**

1. Each cluster has local OpenShift GitOps (Argo CD)
2. Cluster's Argo CD monitors Git repository
3. Cluster autonomously pulls and applies configurations
4. Hub cluster registers managed clusters via ACM
5. Hub provides observability and policy, not deployment

**Advantages:**

- ✅ Cluster autonomy (continues working if hub is down)
- ✅ Familiar pattern (each cluster is self-contained)
- ✅ Works in disconnected scenarios
- ✅ Reduced hub load
- ✅ Clear ownership (cluster manages itself)

**Disadvantages:**

- ❌ Each cluster needs GitOps operator
- ❌ More resource usage per cluster
- ❌ Cluster-specific configuration in Git

**Use Cases:**

- Production clusters (need autonomy)
- Edge/remote sites (may disconnect)
- Development/test clusters
- **Default for this repository**

#### Push Model (Optional)

**How it Works:**

1. Only hub cluster runs OpenShift GitOps
2. Hub's Argo CD connects to managed clusters
3. Hub pushes configurations to managed clusters
4. Managed clusters are passive targets

**Advantages:**

- ✅ Centralized control
- ✅ Less resource usage on managed clusters
- ✅ Single Argo CD instance to manage

**Disadvantages:**

- ❌ Hub is single point of failure
- ❌ Doesn't work when hub disconnected
- ❌ Requires hub-to-cluster connectivity always
- ❌ More complex RBAC management

**Use Cases:**

- Very small clusters (limited resources)
- Fully connected environments
- Hub-managed ephemeral clusters
- **Not currently implemented**

### Cluster Registration Process

#### Bootstrap Flow

1. **Deploy Managed Cluster:**

   ```bash
   # On managed cluster
   cd /path/to/argo-apps
   oc apply -k bootstrap/
   ```

2. **Create Cluster Application:**

   ```bash
   cat <<EOF | oc apply -f -
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: cluster
     namespace: openshift-gitops
   spec:
     project: default
     source:
       repoURL: https://github.com/rbales79/argo-apps.git
       targetRevision: main
       path: roles/sno
       helm:
         valueFiles:
           - ../../values-global.yaml
           - ../../clusters/sets/values-home.yaml
           - ../../clusters/individual-clusters/values-prod.yaml
     destination:
       server: https://kubernetes.default.svc
       namespace: openshift-gitops
   EOF
   ```

3. **Register with Hub (via ACM):**

   ```bash
   # On hub cluster
   oc create -f - <<EOF
   apiVersion: cluster.open-cluster-management.io/v1
   kind: ManagedCluster
   metadata:
     name: prod
   spec:
     hubAcceptsClient: true
   EOF
   ```

4. **Import Cluster:**
   ```bash
   # Get import command from ACM console or CLI
   # Run on managed cluster to complete registration
   ```

### Multi-Cluster Configuration Management

**Kubeconfig Management:**

- Multiple kubeconfig files in `~/.kube/configs/`
- Cluster switching functions: `hub`, `test`, `sno`
- Context validation: `current-cluster`, `cluster-status`
- See: `docs/operations/KUBECONFIG-MANAGEMENT.md`

**Values File Strategy:**

- Cluster set values (home, worklab, cloud)
- Individual cluster values per managed cluster
- Hub cluster has minimal application deployment
- See: ADR 005 (Values Hierarchy)

### Consequences

**Good:**

- ✅ Hub provides centralized observability
- ✅ ACM enables cluster lifecycle automation
- ✅ Pull model provides cluster autonomy
- ✅ Each cluster is self-sufficient
- ✅ Scales to 10+ clusters easily
- ✅ Supports disconnected scenarios
- ✅ Clear separation of management and workload clusters
- ✅ Red Hat support for ACM/MCE

**Bad:**

- ❌ Additional hub cluster required (resource cost)
- ❌ ACM license required (included in OpenShift Platform Plus)
- ❌ More complex than single-cluster setup
- ❌ Each managed cluster runs GitOps operator
- ❌ Cluster registration requires manual steps

**Neutral:**

- 🔄 Pull model default, push model possible but not implemented
- 🔄 Hub cluster typically doesn't run workload applications
- 🔄 ACM/MCE operators consume significant resources on hub
- 🔄 Cluster import process requires kubeconfig access

### Confirmation

Multi-cluster strategy is working correctly if:

1. **Hub Cluster Running:**

   ```bash
   oc get multiclusterhub -n open-cluster-management
   # Should show: Running
   ```

2. **Managed Clusters Registered:**

   ```bash
   oc get managedclusters
   # Should list: prod, test, worklab (with Ready status)
   ```

3. **Local GitOps on Managed Clusters:**

   ```bash
   # On managed cluster (e.g., prod)
   oc get argocd -n openshift-gitops
   # Should show local Argo CD instance
   ```

4. **Cluster Context Switching:**

   ```bash
   hub      # Switch to hub
   prod     # Switch to prod (if function defined)
   current  # Show current cluster
   ```

5. **Applications Deployed Locally:**
   ```bash
   # On managed cluster
   oc get applications.argoproj.io -n openshift-gitops
   # Should show local application deployments
   ```

## Pros and Cons of the Options

### Independent Clusters (No ACM)

- Good: Simplest setup
- Good: No hub cluster required
- Good: Each cluster fully autonomous
- Bad: No centralized observability
- Bad: Manual cluster lifecycle
- Bad: Difficult to enforce policies
- Bad: Poor visibility across fleet

### Hub-and-Spoke with ACM (Chosen)

- Good: Centralized management
- Good: Cluster lifecycle automation
- Good: Policy enforcement
- Good: Fleet-wide observability
- Good: Scales well (10-100+ clusters)
- Bad: Requires additional hub cluster
- Bad: ACM license cost
- Bad: More complex setup

### Full Mesh (All Clusters Peer)

- Good: No single point of failure
- Good: Direct cluster-to-cluster communication
- Bad: Complexity grows exponentially (N² connections)
- Bad: Difficult to manage at scale
- Bad: No clear management authority
- Bad: Inconsistent policy enforcement

### External Management Platform (Rancher, etc.)

- Good: Vendor-agnostic
- Good: Rich UI/UX
- Bad: Additional platform to maintain
- Bad: Not Red Hat supported
- Bad: Another authentication system
- Bad: Doesn't integrate with OpenShift natively

### Cloud-Native Multi-Cluster

- Good: Cloud provider integration
- Good: Managed service options
- Bad: Vendor lock-in
- Bad: Doesn't support on-premise clusters easily
- Bad: Different patterns per cloud provider
- Bad: Cost at scale

## Links

- **Pattern Selection:** [Deployment Options](../deployment/DEPLOYMENT-OPTIONS.md) - Choose single vs multi-cluster
- **Operational Guide:** [ACM Getting Started](../ACM-GETTING-STARTED.md) - Step-by-step ACM setup
- **Kubeconfig Management:** [Kubeconfig Management](../operations/KUBECONFIG-MANAGEMENT.md) - Cluster switching guide
- **Related ADRs:**
  - ADR 002: Validated Patterns Framework (GitOps architecture)
  - ADR 003: Topology Structure (cluster roles)
  - ADR 005: Values Hierarchy (cluster configuration)
- **Red Hat ACM Documentation:** https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/

## Notes

- **Hub Cluster Resources:** Minimum 4 vCPU, 16GB RAM for ACM/MCE
- **Cluster Import:** Requires kubeconfig with cluster-admin access
- **Observability:** ACM observability addon optional, resource-intensive
- **Policy Engine:** ACM policies for governance, security, configuration management
- **Future Enhancement:** Automated cluster provisioning via Hive/Assisted Installer
- **Backup Coordination:** Hub cluster coordinates Kasten K10 backup across managed clusters
