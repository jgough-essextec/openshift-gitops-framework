---
status: "accepted"
date: 2025-11-07
decision-makers:
  - Roy Bales
consulted:
  - Red Hat Validated Patterns Framework
informed:
  - Development Team
---

# ADR 005: Values Hierarchy Pattern

## Context and Problem Statement

As the number of clusters and deployment topologies grew, we needed a consistent way to manage configuration across multiple dimensions:

- **Cluster Sets** (home lab, work lab, cloud providers) with different infrastructure dependencies
- **Topologies** (SNO, Compact, Full) with different resource requirements and HA characteristics
- **Individual Clusters** with specific configurations and enabled applications
- **Global Defaults** that apply across all deployments

Without a clear hierarchy, configuration became duplicated and difficult to maintain. We needed a system that supports:

1. DRY principle (Don't Repeat Yourself)
2. Progressive overrides (specific values override general ones)
3. Clear precedence rules
4. Infrastructure-specific configurations (storage, certificates, secrets)
5. Topology-specific settings (replicas, PDBs, resource limits)

## Decision Drivers

- Eliminate configuration duplication across clusters
- Support multiple infrastructure environments (on-prem, cloud)
- Handle topology differences (node counts, HA requirements)
- Enable per-cluster customization without breaking patterns
- Maintain clarity about which values take precedence
- Support Helm's native values merge behavior

## Considered Options

1. **Flat Structure** - One values file per cluster (original approach)
2. **Two-Level Hierarchy** - Global + Cluster-specific
3. **Three-Level Hierarchy** - Global + Topology + Cluster
4. **Four-Level Hierarchy** - Global + Cluster Set + Topology + Cluster (chosen)
5. **Environment Variables** - Use env vars for all configuration

## Decision Outcome

Chosen option: **Four-Level Hierarchy (Global → Cluster Set → Topology → Cluster)**, because it provides the best balance of flexibility and maintainability.

### Hierarchy Structure

```
values-global.yaml (pattern-wide defaults)
  ↓
clusters/sets/values-<set>.yaml (environment infrastructure)
  ↓
clusters/topologies/values-<topology>.yaml (node count settings)
  ↓
clusters/individual-clusters/values-<cluster>.yaml (specific overrides)
```

### Merge Order

Helm merges values files **left to right**, with later files overriding earlier ones:

```bash
helm install <cluster> ./roles/<topology> \
  -f values-global.yaml \
  -f clusters/sets/values-<set>.yaml \
  -f clusters/topologies/values-<topology>.yaml \
  -f clusters/individual-clusters/values-<cluster>.yaml
```

### File Responsibilities

#### 1. `values-global.yaml` (Pattern Defaults)

**Contains:**

- GitOps repository URL and branch
- Default image registry settings
- Common labels and annotations
- Base application lists (all commented)
- Framework version information

**Example:**

```yaml
clusterGroup:
  name: argo-apps
  gitRepoUrl: https://github.com/rbales79/argo-apps.git
  targetRevision: main

  applicationStacks:
    ai:
      apps:
        # - litellm
        # - ollama
        # - open-webui
```

#### 2. `clusters/sets/values-<set>.yaml` (Infrastructure Environment)

**Contains:**

- Storage provider configuration (TrueNAS, Synology, cloud CSI)
- Certificate authority (Let's Encrypt, internal CA, cloud provider)
- External secrets provider (Infisical, HashiCorp Vault, AWS Secrets Manager)
- DNS provider (Cloudflare, Route53, internal DNS)
- Network policies and CIDR ranges
- Monitoring endpoints

**Examples:**

**Home Lab** (`values-home.yaml`):

```yaml
clusterGroup:
  storage:
    provider: truenas
    truenas:
      api: "https://truenas.example.com"

  certificates:
    provider: letsencrypt
    cloudflare:
      enabled: true

  externalSecrets:
    provider: infisical
```

**Work Lab** (`values-worklab.yaml`):

```yaml
clusterGroup:
  storage:
    provider: synology

  certificates:
    provider: internal-ca

  externalSecrets:
    provider: vault
```

**Cloud** (`values-cloud.yaml`):

```yaml
clusterGroup:
  storage:
    provider: aws-ebs

  certificates:
    provider: aws-acm

  externalSecrets:
    provider: aws-secrets-manager
```

#### 3. `clusters/topologies/values-<topology>.yaml` (Node Count Settings)

**Contains:**

- Default replica counts
- Pod Disruption Budget settings
- Resource requests/limits
- Affinity/anti-affinity rules
- Autoscaling parameters

**Examples:**

**SNO** (`values-sno.yaml`):

```yaml
topology:
  type: sno
  replicas:
    default: 1
    min: 1
    max: 1
  pdb:
    enabled: false # No PDBs on single node
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
```

**Compact** (`values-compact.yaml`):

```yaml
topology:
  type: compact
  replicas:
    default: 2
    min: 1
    max: 3
  pdb:
    enabled: true
    minAvailable: 1
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
```

**Full** (`values-full.yaml`):

```yaml
topology:
  type: full
  replicas:
    default: 3
    min: 2
    max: 5
  pdb:
    enabled: true
    minAvailable: 2
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
```

#### 4. `clusters/individual-clusters/values-<cluster>.yaml` (Cluster Specifics)

**Contains:**

- Cluster name and domain
- Enabled applications (uncommented from lists)
- Cluster admin email
- Timezone
- Specific resource overrides
- Custom configurations

**Example:**

```yaml
clusterGroup:
  name: prod
  domain: prod.example.com
  admin:
    email: admin@example.com

  applicationStacks:
    media:
      enabled: true
      apps:
        - plex # ENABLED
        - sonarr # ENABLED
        - radarr # ENABLED
        # - overseerr    # Disabled
```

### Consequences

**Good:**

- ✅ Eliminates 80%+ configuration duplication
- ✅ Clear precedence rules (specific overrides general)
- ✅ Infrastructure differences isolated to cluster sets
- ✅ Topology settings reusable across environments
- ✅ Easy to add new clusters with minimal configuration
- ✅ Supports multiple infrastructure patterns simultaneously
- ✅ Native Helm values merge behavior (well-understood)

**Bad:**

- ❌ More complex than single values file
- ❌ Requires understanding of merge order
- ❌ Need to know which file to edit for each setting
- ❌ Potential for confusion about value origin

**Neutral:**

- 🔄 Four files to maintain per cluster (but minimal per-file content)
- 🔄 Requires discipline to place settings at correct level

### Confirmation

The values hierarchy is working correctly if:

1. **Deployment succeeds** with all four values files:

   ```bash
   helm template <cluster> ./roles/<topology> \
     -f values-global.yaml \
     -f clusters/sets/values-<set>.yaml \
     -f clusters/topologies/values-<topology>.yaml \
     -f clusters/individual-clusters/values-<cluster>.yaml
   ```

2. **Values merge correctly** - later files override earlier ones:

   ```bash
   # Check merged values
   helm get values <cluster> -n openshift-gitops
   ```

3. **Topology settings apply** - replica counts match topology expectations:

   ```bash
   oc get deployments -A -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.replicas}{"\n"}{end}'
   ```

4. **Infrastructure components enabled** - storage/certs/secrets match cluster set:
   ```bash
   oc get applications.argoproj.io -n openshift-gitops | grep -E 'truenas|cert-manager|external-secrets'
   ```

## Pros and Cons of the Options

### Flat Structure (One File Per Cluster)

- Good: Simple to understand
- Good: Everything in one place
- Bad: Massive duplication (topology settings repeated)
- Bad: Infrastructure settings duplicated across cluster sets
- Bad: Difficult to maintain consistency
- Bad: Hard to apply pattern-wide changes

### Two-Level Hierarchy (Global + Cluster)

- Good: Simple hierarchy
- Good: Easy to understand precedence
- Bad: Still significant duplication
- Bad: Can't separate infrastructure from topology
- Bad: No way to share settings across similar clusters

### Three-Level Hierarchy (Global + Topology + Cluster)

- Good: Eliminates topology duplication
- Good: Reasonable complexity
- Bad: Can't separate infrastructure environments
- Bad: Home lab and work lab settings intermixed
- Bad: Cloud provider settings mixed with on-prem

### Environment Variables

- Good: External to Git repository
- Bad: Not GitOps-friendly
- Bad: Difficult to audit and review
- Bad: No version control
- Bad: Helm doesn't natively support complex env var merging

## Links

- **Implementation:** `docs/VALUES-HIERARCHY.md` - Detailed usage guide
- **Configuration Guide:** `docs/CONFIGURATION-GUIDE.md` - What to modify where
- **Deployment Examples:** `docs/deployment/DEPLOYMENT-OPTIONS.md` - Practical examples
- **Related ADRs:**
  - ADR 002: Validated Patterns Framework
  - ADR 003: Topology Structure
- **Helm Values Documentation:** https://helm.sh/docs/chart_template_guide/values_files/

## Notes

- **File Locations Changed (ADR 003):** Values files moved from repo root to `clusters/` subdirectories for better organization
- **Topology Charts Removed:** Empty `charts/topology/` directories removed - configuration belongs in values files
- **Bootstrap Process:** Initial bootstrap uses only cluster-specific values file, hierarchy applied after GitOps takes over
- **Values Validation:** Future enhancement - JSON Schema validation for each hierarchy level
