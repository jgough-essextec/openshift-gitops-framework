# Cluster Values Organization

This directory contains all cluster-specific values files for the GitOps deployment.

## 📁 Directory Structure

```text
clusters/
├── individual-clusters/    # Specific cluster configurations
│   ├── values-hub.yaml
│   ├── values-prod.yaml
│   └── values-test.yaml
│
├── sets/                   # Logical cluster groupings
│   ├── values-cloud.yaml
│   ├── values-home.yaml
│   └── values-worklab.yaml
│
└── topologies/            # Topology-based defaults
    ├── values-compact.yaml
    └── values-full.yaml
```

**Global values:** `values-global.yaml` (kept at repo root)

## 📝 File Types

### Individual Clusters

Cluster-specific values files for concrete deployments:

- **values-hub.yaml** - Hub/management cluster (3-node, ACM)
- **values-prod.yaml** - Production cluster (SNO)
- **values-test.yaml** - Testing cluster (SNO)

These files contain:

- Cluster name and domain
- Enabled applications
- Cluster-specific overrides
- Network configuration
- Storage settings

### Cluster Sets

Logical groupings that can be applied to multiple clusters:

- **values-home.yaml** - Home lab environment settings
- **values-worklab.yaml** - Work lab environment settings
- **values-cloud.yaml** - Cloud-hosted cluster settings

These define:

- Environment-wide policies
- Shared application lists
- Common infrastructure components

### Topologies

Topology-based defaults that define resource sizing and replica counts:

- **values-compact.yaml** - 3-node clusters (2-3 replicas, PDB enabled)
- **values-full.yaml** - 6+ node clusters (3+ replicas, full HA)

**Note:** SNO (Single Node OpenShift) topology is defined in `roles/sno/values.yaml`

These define:

- Default replica counts
- PodDisruptionBudget strategy
- Resource requests/limits
- Storage sizing

## 🔄 Values Hierarchy

Values are merged in the following order (later values override earlier):

1. **Global defaults** (`values-global.yaml` at repo root)
2. **Topology defaults** (`clusters/topologies/values-<topology>.yaml`)
3. **Cluster set values** (`clusters/sets/values-<set>.yaml`)
4. **Individual cluster values** (`clusters/individual-clusters/values-<cluster>.yaml`)
5. **Chart-specific values** (in each chart's `values.yaml`)

## 🎯 Usage Examples

### Bootstrap a Cluster

```bash
# Using individual cluster values
helm template hub ./roles/hub -f clusters/individual-clusters/values-hub.yaml

# Using topology + cluster
helm template prod ./roles/sno \
  -f clusters/topologies/values-compact.yaml \
  -f clusters/individual-clusters/values-prod.yaml
```

### ACM Deployment

```bash
# Apply cluster-specific values for ACM pull model
oc apply -f acm/pull-model/policies/ \
  -f clusters/individual-clusters/values-test.yaml
```

### Adding a New Cluster

1. Copy an existing cluster values file
2. Update cluster name and domain
3. Adjust enabled applications
4. Reference appropriate topology file
5. Optionally assign to a cluster set

## 📋 Reference

- **Architecture**: See `docs/DETAILED-OVERVIEW.md`
- **Values Hierarchy**: See `docs/VALUES-HIERARCHY.md`
- **Application Management**: See `docs/APP-MANAGEMENT-QUICK-REF.md`
- **Topology Guide**: See `docs/decisions/ADR-003-topology-structure.md`

## 🔍 Finding Values

### Which file should I edit?

| What you're changing                   | File to edit                                |
| -------------------------------------- | ------------------------------------------- |
| Enable/disable app on specific cluster | `individual-clusters/values-<cluster>.yaml` |
| Change app config for all clusters     | `values-global.yaml` (repo root)            |
| Set environment-wide defaults          | `sets/values-<set>.yaml`                    |
| Adjust replica counts by topology      | `topologies/values-<topology>.yaml`         |
| Change topology sizing                 | `roles/<topology>/values.yaml`              |

### Search for a value

```bash
# Find where a value is defined
grep -r "applicationStacks" clusters/

# Find cluster-specific config
grep -r "cluster_name" clusters/individual-clusters/

# Find topology defaults
grep -r "replicas" clusters/topologies/
```

## 🚀 Quick Reference

### Common Operations

**Enable an application:**

```yaml
# In clusters/individual-clusters/values-<cluster>.yaml
clusterGroup:
  applicationStacks:
    ai:
      enabled: true
      apps:
        - ollama # Uncomment to enable
        # - litellm       # Commented = disabled
```

**Change replica count:**

```yaml
# In clusters/topologies/values-<topology>.yaml
topology:
  replicas:
    default: 3
    database: 3
```

**Set cluster domain:**

```yaml
# In clusters/individual-clusters/values-<cluster>.yaml
cluster:
  name: prod
  top_level_domain: roybales.com
```

## 📌 Important Notes

1. **values-global.yaml** stays at repo root for backward compatibility
2. **values-secret.yaml.template** stays at repo root (not tracked in git)
3. SNO topology values are in `roles/sno/values.yaml` (not in clusters/topologies/)
4. Bootstrap process references these paths in Argo CD Application manifests

## 🔗 Related Documentation

- [Validated Patterns Framework](/.github/copilot-instructions.md)
- [Values Hierarchy](../docs/VALUES-HIERARCHY.md)
- [Change Management](../docs/CHANGE-MANAGEMENT.md)
