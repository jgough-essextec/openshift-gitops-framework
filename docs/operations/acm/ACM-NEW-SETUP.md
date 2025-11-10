# Advanced Cluster Management (ACM) for OpenShift

**Manage multiple OpenShift clusters with Red Hat ACM**

## 📁 Directory Structure (NEW!)

This directory has been reorganized for clarity:

```text
acm/
├── common/          # Shared resources (ManagedClusterSet, Placement, labels)
├── push-model/      # Hub pushes configurations to clusters
├── pull-model/      # Clusters pull configurations from Git
├── docs/            # Detailed documentation
├── deploy-acm-config.sh     # Automated setup script
├── cleanup-acm-config.sh    # Cleanup script
└── README-ORGANIZATION.md   # Complete organization guide
```

## 🚀 Quick Start

### Step 1: Deploy Common Resources (Required First!)

```bash
cd acm/common
oc apply -f 01-managedclusterset.yaml
oc apply -f 02-managedclustersetbinding.yaml
oc apply -f 03-placement-platform.yaml
bash 04-label-clusters.sh
```

### Step 2: Choose Your Model

#### Push Model (Hub Pushes to Clusters)

**Best for:** Small fleets (< 10 clusters), centralized control

```bash
cd acm/push-model
oc apply -f 05-gitopscluster.yaml
sleep 15  # Wait for cluster secrets
oc apply -f homelab-platform-simple.yaml
```

#### Pull Model (Clusters Pull from Git)

**Best for:** Large fleets (10+ clusters), cluster autonomy

```bash
cd acm/pull-model/policies
bash deploy-policies.sh
```

## 📊 Model Comparison

| Aspect          | Push Model           | Pull Model               |
| --------------- | -------------------- | ------------------------ |
| **Control**     | Centralized (Hub)    | Distributed (Clusters)   |
| **Scalability** | Good (< 10 clusters) | Excellent (10+ clusters) |
| **Setup**       | Simpler              | More complex             |
| **Hub Load**    | Higher               | Lower                    |
| **Network**     | Hub → Clusters       | Clusters → Git           |

## 📚 Documentation

- **README-ORGANIZATION.md** - Complete directory guide & decision tree
- **docs/QUICK-START.md** - 5-minute deployment guide
- **docs/MODEL-COMPARISON.md** - Detailed architecture comparison
- **docs/PULL-MODEL-SETUP.md** - Pull model step-by-step setup

## 🔧 Automation Scripts

### Deployment

```bash
./deploy-acm-config.sh    # Deploy common resources automatically
```

### Cleanup

```bash
./cleanup-acm-config.sh   # Remove all ACM configurations
```

## 🏷️ Cluster Labeling

Clusters must be labeled to participate in placement:

```bash
# Required label
oc label managedcluster <cluster-name> \
  cluster.open-cluster-management.io/clusterset=homelab

# Optional labels for advanced placement
oc label managedcluster <cluster-name> env=prod|test
oc label managedcluster <cluster-name> topology=sno|compact|full
```

## 🔍 Verification

```bash
# Check placements
oc get placement -n openshift-gitops

# Check placement decisions
oc get placementdecision -n openshift-gitops

# Check ApplicationSets (push model)
oc get applicationset -n openshift-gitops

# Check policies (pull model)
oc get policies -A
```

## 🆘 Troubleshooting

### Push Model: No Applications Generated

```bash
# Check GitOpsCluster
oc get gitopscluster -n openshift-gitops

# Check cluster secrets
oc get secrets -n openshift-gitops \
  -l apps.open-cluster-management.io/acm-cluster=true

# Describe ApplicationSet
oc describe applicationset homelab-platform-simple -n openshift-gitops
```

### Pull Model: Policies Not Compliant

```bash
# Check policy status
oc get policies -A

# Describe specific policy
oc describe policy install-gitops -n <namespace>

# Check managed cluster
oc get managedcluster <cluster-name> -o yaml
```

## 📖 Migration Guide

**Switching from Push to Pull:**

1. Delete push model resources: `cd push-model && oc delete -f .`
2. Deploy pull model: `cd pull-model/policies && bash deploy-policies.sh`

**Switching from Pull to Push:**

1. Delete policies: `oc delete policy install-gitops configure-argo-rbac -n <namespace>`
2. Deploy push model: See Quick Start above

## 🎯 Next Steps

1. ✅ Review `README-ORGANIZATION.md` for complete guide
2. ✅ Choose push or pull model based on your needs
3. ✅ Deploy common resources
4. ✅ Deploy your chosen model
5. ✅ Verify deployments

---

**For detailed information, see:** `README-ORGANIZATION.md`
