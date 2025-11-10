# ACM Directory Organization

This directory contains resources for managing OpenShift clusters via Red Hat Advanced Cluster Management (ACM).

## 📁 Directory Structure

```
acm/
├── common/                   # Shared resources (both push & pull)
│   ├── 01-managedclusterset.yaml
│   ├── 02-managedclustersetbinding.yaml
│   ├── 03-placement-platform.yaml
│   └── 04-label-clusters.sh
│
├── push-model/              # Hub pushes to managed clusters
│   ├── 05-gitopscluster.yaml
│   ├── homelab-platform-simple.yaml
│   ├── homelab-platform-applicationset.yaml
│   ├── homelab-platform-applicationset-template.yaml
│   ├── homelab-platform-components-applicationset.yaml
│   ├── homelab-platform-components-applicationset-template.yaml
│   └── test-simple-list.yaml
│
├── pull-model/              # Clusters pull from Git themselves
│   └── policies/
│       ├── 01-install-gitops-policy.yaml
│       ├── 02-bootstrap-application-policy.yaml
│       ├── 02-bootstrap-application-policy-test.yaml
│       ├── 03-configure-argo-rbac-policy.yaml
│       ├── deploy-policies.sh
│       └── README.md
│
├── docs/                    # Documentation
│   ├── MODEL-COMPARISON.md
│   ├── PULL-MODEL-SETUP.md
│   ├── QUICK-START.md
│   ├── DEPLOYMENT-STATUS.md
│   ├── EXTRACTION-SUMMARY.md
│   ├── INDEX.md
│   ├── SUMMARY.md
│   └── WORKING-CONFIG.md
│
├── README.md                # Main ACM documentation
├── README-ORGANIZATION.md   # This file
├── cleanup-acm-config.sh    # Cleanup script
├── deploy-acm-config.sh     # Deployment script
└── 03-placement-examples.yaml  # Reference examples
```

## 🔄 Deployment Models

### Push Model (Hub-Centric)

**Location:** `push-model/`

**How it works:**

1. Hub cluster's Argo CD manages all deployments
2. GitOpsCluster resource creates cluster secrets in hub's Argo CD
3. ApplicationSets on hub generate Applications that deploy to managed clusters
4. Hub "pushes" configurations to managed clusters

**Use when:**

- Small cluster fleet (< 10 clusters)
- Centralized control desired
- Consistent configuration across all clusters

**Quick start:**

```bash
# 1. Deploy common resources
cd acm/common
oc apply -f 01-managedclusterset.yaml
oc apply -f 02-managedclustersetbinding.yaml
oc apply -f 03-placement-platform.yaml
bash 04-label-clusters.sh

# 2. Deploy push model
cd ../push-model
oc apply -f 05-gitopscluster.yaml
sleep 15  # Wait for cluster secrets
oc apply -f homelab-platform-simple.yaml
```

### Pull Model (Cluster-Autonomous)

**Location:** `pull-model/`

**How it works:**

1. ACM policies install GitOps operator on each managed cluster
2. Policies create bootstrap Application on each cluster
3. Each cluster's local Argo CD pulls from Git
4. Clusters "pull" their own configurations

**Use when:**

- Large cluster fleet (10+ clusters)
- Cluster autonomy desired
- Network isolation requirements
- Air-gapped environments

**Quick start:**

```bash
# 1. Deploy common resources
cd acm/common
oc apply -f 01-managedclusterset.yaml
oc apply -f 02-managedclustersetbinding.yaml
oc apply -f 03-placement-platform.yaml
bash 04-label-clusters.sh

# 2. Deploy pull model policies
cd ../pull-model/policies
bash deploy-policies.sh
```

## 🎯 Common Resources (Required for Both Models)

**Location:** `common/`

These resources are prerequisites for either deployment model:

1. **ManagedClusterSet** (`01-managedclusterset.yaml`)

   - Groups managed clusters together
   - Name: `homelab`

2. **ManagedClusterSetBinding** (`02-managedclustersetbinding.yaml`)

   - Binds the cluster set to `openshift-gitops` namespace
   - Allows Argo CD to deploy to managed clusters

3. **Placement** (`03-placement-platform.yaml`)

   - Selects which clusters to target
   - Uses labels: `cluster.open-cluster-management.io/clusterset=homelab`

4. **Label Script** (`04-label-clusters.sh`)
   - Helper script to label clusters for placement
   - Labels: `clusterset=homelab`, `env=prod|test`, `topology=sno|compact|full`

## 📊 Model Comparison

| Aspect               | Push Model                    | Pull Model                   |
| -------------------- | ----------------------------- | ---------------------------- |
| **Control**          | Centralized (Hub)             | Distributed (Each cluster)   |
| **Hub Load**         | Higher (manages all clusters) | Lower (only policies)        |
| **Network**          | Hub → Clusters outbound       | Clusters → Git inbound       |
| **Scalability**      | Good (< 10 clusters)          | Excellent (10+ clusters)     |
| **Security**         | Hub has cluster access        | Clusters authenticate to Git |
| **Failure Domain**   | Hub failure affects all       | Isolated per cluster         |
| **Setup Complexity** | Lower                         | Higher                       |

## 🚀 Quick Decision Guide

**Choose Push Model if:**

- ✅ You have < 10 clusters
- ✅ You want centralized control
- ✅ You trust hub cluster access
- ✅ Simpler setup is priority

**Choose Pull Model if:**

- ✅ You have 10+ clusters
- ✅ You need cluster autonomy
- ✅ You have network restrictions
- ✅ You want isolated failure domains

## 📖 Documentation

Detailed documentation available in `docs/`:

- **MODEL-COMPARISON.md** - Detailed architecture comparison
- **PULL-MODEL-SETUP.md** - Step-by-step pull model setup
- **QUICK-START.md** - Fast deployment guide
- **DEPLOYMENT-STATUS.md** - Current deployment state
- **EXTRACTION-SUMMARY.md** - Configuration extraction notes
- **INDEX.md** - Documentation index
- **SUMMARY.md** - Feature summary
- **WORKING-CONFIG.md** - Working configuration examples

## 🔧 Scripts

### deploy-acm-config.sh

Automated deployment script that:

- Detects which resources are already deployed
- Applies resources in correct order
- Waits for readiness
- Validates deployment

### cleanup-acm-config.sh

Cleanup script that:

- Removes ApplicationSets and Applications
- Deletes GitOpsCluster
- Removes Placements
- Cleans up bindings and cluster sets

## 🏷️ Cluster Labels

Clusters should be labeled with:

```bash
# Required for placement
oc label managedcluster <cluster-name> cluster.open-cluster-management.io/clusterset=homelab

# Optional for advanced placement
oc label managedcluster <cluster-name> env=prod|test|dev
oc label managedcluster <cluster-name> topology=sno|compact|full
oc label managedcluster <cluster-name> region=us-east|us-west|europe
```

## 🔍 Troubleshooting

### Push Model Issues

**No Applications Generated:**

```bash
# Check GitOpsCluster
oc get gitopscluster -n openshift-gitops

# Check cluster secrets
oc get secrets -n openshift-gitops -l apps.open-cluster-management.io/acm-cluster=true

# Check ApplicationSet
oc get applicationset -n openshift-gitops
oc describe applicationset homelab-platform-simple -n openshift-gitops
```

### Pull Model Issues

**Policies Not Compliant:**

```bash
# Check policy status
oc get policies -A

# Check policy details
oc describe policy <policy-name> -n <namespace>

# Check managed cluster status
oc get managedcluster <cluster-name> -o yaml
```

## 📚 Related Documentation

- [Red Hat ACM Documentation](https://access.redhat.com/documentation/en-us/red_hat_advanced_cluster_management_for_kubernetes/)
- [OpenShift GitOps Documentation](https://docs.openshift.com/gitops/)
- [Argo CD ApplicationSet Documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/)

## 🤝 Contributing

When adding new resources:

1. Place push model resources in `push-model/`
2. Place pull model resources in `pull-model/`
3. Place shared resources in `common/`
4. Update this README with new resources
5. Update relevant documentation in `docs/`
