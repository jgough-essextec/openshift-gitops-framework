# ACM Deployment Models - Quick Comparison

## Overview

This repository supports **three deployment models** for managing OpenShift clusters via ACM:

| Model      | Description                    | Best For                          |
| ---------- | ------------------------------ | --------------------------------- |
| **Push**   | Hub pushes to managed clusters | Small fleets, centralized control |
| **Pull**   | Each cluster pulls from Git    | Large fleets, cluster autonomy    |
| **Hybrid** | Combine push + pull approaches | Mixed workloads                   |

## Architecture Diagrams

### Push Model (Current Setup)

```
┌─────────────────────────────────────────────────────────┐
│ Hub Cluster (hub.roybales.com)                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ OpenShift GitOps (Argo CD)                       │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────┐    │  │
│  │  │ ACM Integration                          │    │  │
│  │  │  - GitOpsCluster resource                │    │  │
│  │  │  - Cluster secrets auto-created          │    │  │
│  │  └─────────────────────────────────────────┘    │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────┐    │  │
│  │  │ homelab-platform-simple ApplicationSet   │    │  │
│  │  │  - Clusters generator                    │    │  │
│  │  │  - Matrix with component list            │    │  │
│  │  └─────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Applications Generated:                                │
│  ├─ test-external-secrets-operator ─────┐              │
│  ├─ test-certificates                   │              │
│  ├─ test-openshift-nfd                  │              │
│  └─ (5 more...)                         │              │
└──────────────────────────────────────────┼──────────────┘
                                           │
                                           ▼ Push via Argo CD
                                  ┌────────────────────────┐
                                  │ Test Cluster           │
                                  │ (test.roybales.com)    │
                                  │                        │
                                  │ Platform components    │
                                  │ deployed and managed   │
                                  └────────────────────────┘
```

### Pull Model

```
┌─────────────────────────────────────────────────────────┐
│ Hub Cluster (hub.roybales.com)                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ACM Policies                                      │  │
│  │  1. Install GitOps operator on managed clusters  │  │
│  │  2. Create bootstrap Application                 │  │
│  │  3. Configure RBAC                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Policies enforce configuration ───────┐                │
└────────────────────────────────────────┼────────────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        ▼                ▼                ▼
            ┌──────────────────┐  ┌──────────────────┐  │
            │ Test Cluster     │  │ Prod Cluster     │  │
            │                  │  │                  │  │
            │ GitOps Installed │  │ GitOps Installed │  │
            │       ▼          │  │       ▼          │  │
            │ Bootstrap App    │  │ Bootstrap App    │  │
            │       ▼          │  │       ▼          │  │
            │ Pulls from Git◄──┼──┼───Git Repo       │  │
            │       ▼          │  │       ▼          │  │
            │ ApplicationSets  │  │ ApplicationSets  │  │
            │       ▼          │  │       ▼          │  │
            │ Platform Apps    │  │ Platform Apps    │  │
            └──────────────────┘  └──────────────────┘  │
            Each cluster manages itself autonomously    │
            └─────────────────────────────────────────────┘
```

### Hybrid Model

```
┌─────────────────────────────────────────────────────────┐
│ Hub Cluster - Push Model for Platform                   │
│                                                          │
│  homelab-platform ApplicationSet                        │
│  ├─ test-external-secrets-operator  ─────┐              │
│  ├─ test-certificates                    │              │
│  ├─ prod-external-secrets-operator       │              │
│  └─ prod-certificates                    │              │
└──────────────────────────────────────────┼──────────────┘
                                           │ Push
                        ┌──────────────────┴───────────────┐
                        ▼                                  ▼
            ┌──────────────────┐              ┌──────────────────┐
            │ Test Cluster     │              │ Prod Cluster     │
            │                  │              │                  │
            │ Platform (Hub)   │              │ Platform (Hub)   │
            │       +          │              │       +          │
            │ Apps (Local) ◄───┼──Git Repo──► │ Apps (Local)     │
            │                  │              │                  │
            │ test-ai          │              │ prod-media       │
            │ test-media       │              │ prod-ai          │
            └──────────────────┘              └──────────────────┘
            Pull model for applications
```

## Feature Comparison

| Feature                  | Push Model              | Pull Model                | Hybrid               |
| ------------------------ | ----------------------- | ------------------------- | -------------------- |
| **Argo CD Instances**    | 1 (hub only)            | N (each cluster)          | 1 + N                |
| **Control Point**        | Centralized             | Distributed               | Mixed                |
| **Hub Failure Impact**   | ❌ All deployments stop | ✅ Clusters continue      | ⚠️ Platform affected |
| **Network Requirements** | Hub → All clusters      | None (Git only)           | Hub → All clusters   |
| **Setup Complexity**     | ⭐ Low                  | ⭐⭐ Medium               | ⭐⭐⭐ High          |
| **RBAC Complexity**      | ⭐ Low                  | ⭐⭐ Medium               | ⭐⭐ Medium          |
| **Cluster Autonomy**     | ❌ None                 | ✅ Full                   | ⚡ Partial           |
| **Observability**        | ⭐⭐⭐ Easy (single UI) | ⭐⭐ Moderate             | ⭐⭐ Moderate        |
| **Maintenance**          | ⭐ Low (1 instance)     | ⭐⭐⭐ High (N instances) | ⭐⭐ Medium          |
| **Policy Enforcement**   | Via ApplicationSet      | Via ACM Policies          | Both                 |

## Implementation Files

### Push Model (✅ Currently Deployed)

```
acm/
├── 01-managedclusterset.yaml          # Homelab ClusterSet
├── 02-managedclustersetbinding.yaml   # Bind to openshift-gitops
├── 03-placement-platform.yaml         # Select clusters
├── 05-gitopscluster.yaml              # ⭐ ACM-Argo bridge
├── homelab-platform-simple.yaml       # ⭐ Working ApplicationSet
├── WORKING-CONFIG.md                  # Technical docs
├── DEPLOYMENT-STATUS.md               # Current status
└── QUICK-START.md                     # Fast deployment
```

### Pull Model (📋 Ready to Deploy)

```
acm/policies/
├── 01-install-gitops-policy.yaml           # Install GitOps on clusters
├── 02-bootstrap-application-policy.yaml    # Create bootstrap apps
├── 03-configure-argo-rbac-policy.yaml      # Configure RBAC
├── deploy-policies.sh                      # Automated deployment
├── README.md                               # Policy documentation
└── PULL-MODEL-SETUP.md                     # Complete guide
```

### Hybrid Model (💡 Conceptual)

Combine both approaches:

- Use push model files for platform components
- Use pull model policies for application stacks
- Configure `values-<cluster>.yaml` appropriately

## Decision Guide

### Choose Push Model When:

✅ **Cluster count**: < 10 clusters
✅ **Network**: All clusters in same network/VPC
✅ **Hub availability**: Hub cluster is highly available
✅ **Control**: Need centralized control and visibility
✅ **Team size**: Small team managing all clusters
✅ **Complexity tolerance**: Prefer simple architecture

**Example**: Homelab with 3 clusters, single administrator

### Choose Pull Model When:

✅ **Cluster count**: > 10 clusters or growing rapidly
✅ **Network**: Clusters in different networks/regions
✅ **Hub availability**: Hub may have downtime
✅ **Autonomy**: Clusters should be self-sufficient
✅ **Team size**: Multiple teams, each managing clusters
✅ **Complexity tolerance**: Can handle distributed systems

**Example**: Multi-region deployment, each team manages their clusters

### Choose Hybrid Model When:

✅ **Mixed requirements**: Different needs for platform vs apps
✅ **Platform centralization**: Want consistent platform across clusters
✅ **App autonomy**: Teams control their own applications
✅ **Risk mitigation**: Platform can fail without affecting apps
✅ **Gradual migration**: Transitioning from push to pull

**Example**: Enterprise with standardized platform, team-specific apps

## Quick Start

### Deploy Push Model (Current)

```bash
cd /workspaces/argo-apps/acm
./deploy-acm-config.sh
oc apply -f 05-gitopscluster.yaml
oc apply -f homelab-platform-simple.yaml
```

**See**: `QUICK-START.md` for detailed guide

### Deploy Pull Model

```bash
cd /workspaces/argo-apps/acm/policies
./deploy-policies.sh
```

**See**: `PULL-MODEL-SETUP.md` for detailed guide

### Deploy Hybrid Model

```bash
# 1. Deploy push model for platform
cd /workspaces/argo-apps/acm
./deploy-acm-config.sh
oc apply -f 05-gitopscluster.yaml
oc apply -f homelab-platform-simple.yaml

# 2. Deploy pull model for applications
cd policies
./deploy-policies.sh

# 3. Update values files to disable platform components locally
# Edit clusters/individual-clusters/values-test.yaml, clusters/individual-clusters/values-prod.yaml:
#   platformComponents: {}  # Disabled - hub manages
#   applicationStacks:      # Enabled - local management
#     ai: { enabled: true }
```

**See**: `PULL-MODEL-SETUP.md` for hybrid configuration

## Migration Paths

### Push → Pull

1. Deploy pull model policies
2. Wait for bootstrap Applications to sync
3. Delete push model ApplicationSets
4. Update values files (remove `destination.server`)

### Pull → Push

1. Deploy push model resources (ClusterSet, GitOpsCluster, ApplicationSet)
2. Delete bootstrap Applications on managed clusters
3. Update values files (add `destination.server`)
4. Remove pull model policies

### Current → Hybrid

1. Keep existing push model for platform
2. Deploy pull model policies for applications
3. Update values files to split responsibilities
4. Monitor both systems

## Monitoring

### Push Model

```bash
# From hub cluster
oc get applications -n openshift-gitops | grep -E "test-|prod-"
oc get applicationset homelab-platform-simple -n openshift-gitops
```

### Pull Model

```bash
# From hub cluster (policies)
oc get policy -n open-cluster-management-policies

# On each cluster (applications)
test; oc get application cluster -n openshift-gitops
prod; oc get application cluster -n openshift-gitops
```

### Hybrid Model

Monitor both push and pull components separately.

## Documentation Index

| Document               | Purpose                    | Model |
| ---------------------- | -------------------------- | ----- |
| `README.md`            | Main ACM guide             | All   |
| `QUICK-START.md`       | 5-minute push setup        | Push  |
| `WORKING-CONFIG.md`    | Technical deep dive        | Push  |
| `DEPLOYMENT-STATUS.md` | Current deployment         | Push  |
| `PULL-MODEL-SETUP.md`  | Pull model complete guide  | Pull  |
| `policies/README.md`   | ACM policies documentation | Pull  |
| `MODEL-COMPARISON.md`  | This document              | All   |
| `INDEX.md`             | File index                 | All   |

## Recommendations

### For Your Homelab (Current Setup)

✅ **Push Model** - You're using the right approach!

**Reasoning**:

- Only 2-3 clusters (sno, test, hub)
- Single administrator
- All clusters in same network
- Want centralized visibility
- Keep it simple

**Next Steps**:

1. Validate test cluster deployment
2. Add prod cluster to homelab clusterset
3. Monitor platform components
4. Consider hybrid for application stacks later

### Future Considerations

**When to reconsider**:

- Growing beyond 5 clusters
- Adding clusters in different networks
- Multiple teams managing clusters
- Need for cluster autonomy increases

**Migration path**: Start with hybrid (platform push, apps pull)

## Support

- **Push Model Issues**: See `WORKING-CONFIG.md` troubleshooting
- **Pull Model Issues**: See `policies/README.md` troubleshooting
- **General ACM**: See `README.md`
- **Quick Questions**: See `QUICK-START.md`

---

**Current Setup**: ✅ Push Model (Working)
**Alternative**: 📋 Pull Model (Ready to deploy)
**Future**: 💡 Hybrid Model (Documented)
