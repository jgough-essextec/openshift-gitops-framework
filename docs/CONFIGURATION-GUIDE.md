# Configuration Guide: Templates vs User-Specific Files

> **📋 Strategic Context:** See [ADR 005: Values Hierarchy Pattern](./decisions/005-values-hierarchy-pattern.md) for the architectural decision behind the configuration system.

Understanding what to modify and what to leave as-is in the argo-apps repository.

**Last Updated:** 2025-11-07

---

## 🎯 Overview

This guide helps you understand the distinction between:

- **Framework/Template Files** - Core pattern files (DO NOT MODIFY)
- **Configuration Files** - Cluster-specific files (CUSTOMIZE)
- **Extension Files** - Optional additions (EXTEND AS NEEDED)

---

## 📦 File Categories

### 🔒 Framework Files (DO NOT MODIFY)

These files are part of the Validated Patterns framework and should not be edited unless you're contributing to the framework itself.

#### Role Templates

**Location:** `roles/*/templates/`

**Files:**

```
roles/
├── sno/templates/
│   ├── platform-applicationset.yaml
│   ├── ai-applicationset.yaml
│   ├── media-applicationset.yaml
│   ├── home-automation-applicationset.yaml
│   ├── productivity-applicationset.yaml
│   └── infrastructure-applicationset.yaml
├── compact/templates/
│   └── (same files)
└── full/templates/
    └── (same files)
```

**Purpose:**

- Deploy ApplicationSet charts
- Create Application resources
- Bootstrap GitOps workflow

**Why Not Modify:**

- Templates are synced across all roles using `scripts/sync-role-templates.sh`
- Changes will be overwritten during sync
- Breaks upgrade path for framework updates
- Makes it difficult to merge upstream changes

**How to Customize:**

- Modify values files instead (see Configuration Files below)
- Use Helm templating parameters
- Override via `clusterGroup` values

#### Chart Helper Templates

**Location:** `charts/*/templates/_helpers.tpl`

**Purpose:**

- Standard Helm template functions
- Naming conventions
- Label generation
- Selector patterns

**Why Not Modify:**

- Ensures consistency across charts
- Breaks chart upgrades
- Makes troubleshooting difficult

**How to Customize:**

- Extend with additional functions if needed
- Follow naming conventions in existing helpers
- Test thoroughly if modifications are necessary

#### ApplicationSet Templates

**Location:** `charts/applications/*/templates/applicationset.yaml`

**Purpose:**

- Generate Application resources for each app
- Control sync waves
- Manage namespace creation
- Apply common configuration

**Why Not Modify:**

- Core pattern architecture
- Affects all apps in domain
- Breaks ApplicationSet generation

**How to Customize:**

- Add apps via values files (see Configuration Files)
- Use `managedNamespaceMetadata` for namespace labels
- Adjust sync waves only if you understand implications

#### CRD Definitions

**Location:** `charts/*/crds/`

**Purpose:**

- Custom Resource Definitions for operators
- Installed before other resources
- Define API schemas

**Why Not Modify:**

- Vendor-provided definitions
- Breaking changes to API
- Helm doesn't template CRDs

**How to Customize:**

- Don't customize CRDs
- Use custom resources (CRs) to configure
- Submit upstream PRs for CRD changes

---

### ✏️ Configuration Files (CUSTOMIZE THESE)

These files are intended to be modified for your specific deployment.

#### Cluster Values Files

**Location:** `clusters/individual-clusters/values-<cluster>.yaml`

**Files:**

```
clusters/individual-clusters/
├── values-sno.yaml      # Single Node OpenShift cluster
├── values-hub.yaml      # Hub/management cluster
├── values-prod.yaml     # Production cluster
└── values-test.yaml     # Test cluster
```

**Purpose:**

- Cluster-specific configuration
- Enable/disable applications
- Configure platform components
- Set cluster-specific parameters

**What to Customize:**

```yaml
clusterGroup:
  name: sno # Cluster identifier
  domain: example.com # Base domain

  # Platform components - enable/disable
  platformComponents:
    externalSecretsOperator:
      enabled: true
    verticalPodAutoscaler:
      enabled: true
    # ... enable what you need

  # Applications - uncomment to enable
  applicationStacks:
    ai:
      enabled: true
      apps:
        - ollama # Enabled
        # - litellm      # Disabled (commented)

    media:
      enabled: true
      apps:
        - plex
        - sonarr
        # ... etc

  # Storage configuration
  storage:
    truenas:
      enabled: true
      apiUrl: "https://truenas.example.com"

  # Network configuration
  network:
    metallb:
      enabled: true
      ipAddressPool: "192.168.1.100-192.168.1.110"

  # Certificates
  certificates:
    letsencrypt:
      enabled: true
      email: "admin@example.com"
```

**Best Practices:**

- Start with one cluster config (e.g., test)
- Copy and modify for other clusters
- Comment out unused apps (keep for reference)
- Document custom values with inline comments
- Use descriptive cluster names

#### Cluster Set Values Files

**Location:** `clusters/sets/values-<set>.yaml`

**Files:**

```
clusters/sets/
├── values-home.yaml     # Home lab cluster set
├── values-worklab.yaml  # Work lab cluster set
└── values-cloud.yaml    # Cloud cluster set
```

**Purpose:**

- Share configuration across multiple clusters
- Define environment-specific defaults
- Reduce duplication

**What to Customize:**

```yaml
clusterGroup:
  # Common settings for all clusters in this set
  platformComponents:
    # Shared platform component configuration

  storage:
    # Common storage provider settings

  network:
    # Network settings applicable to all clusters in set
```

**Best Practices:**

- Use for common configurations across clusters
- Override in individual cluster files when needed
- Keep set-specific logic (not cluster-specific)

#### Topology Values Files

**Location:** `clusters/topologies/values-<topology>.yaml`

**Files:**

```
clusters/topologies/
├── values-compact.yaml  # 3-node compact topology
└── values-full.yaml     # 6+ node full topology
```

**Purpose:**

- Define topology-specific defaults
- Set replica counts based on node count
- Configure Pod Disruption Budgets
- Resource sizing

**What to Customize:**

```yaml
topology:
  type: compact # or full

  replicas:
    default: 2 # Default replica count
    min: 1
    max: 3

  pdb:
    enabled: true
    minAvailable: 1

  resources:
    default:
      requests:
        memory: "256Mi"
        cpu: "100m"
```

**Best Practices:**

- Match topology to cluster size
- Compact: 3 nodes, 2 replicas, PDB minAvailable=1
- Full: 6+ nodes, 3 replicas, PDB minAvailable=2
- Override in app charts if specific needs

#### Secret Values File

**Location:** `values-secret.yaml` (git-ignored)

**Template:** `values-secret.yaml.template`

**Purpose:**

- Store sensitive configuration locally
- Avoid committing secrets to Git
- Override secret values per cluster

**What to Customize:**

```yaml
clusterGroup:
  # Sensitive values that shouldn't be in Git
  externalSecrets:
    provider: vault # or aws, azure, etc.
    backend:
      vault:
        server: "https://vault.example.com"
        auth:
          token: "s.XXXXXXXXXXXXX" # Never commit!

  storage:
    truenas:
      apiKey: "TRUENAS_API_KEY" # Never commit!

  certificates:
    letsencrypt:
      # Can use external-secrets-operator instead
```

**Best Practices:**

- Copy template: `cp values-secret.yaml.template values-secret.yaml`
- Add to `.gitignore` (already done)
- Use external-secrets-operator when possible
- Rotate secrets regularly
- Document required secrets in README

#### Application Chart Values

**Location:** `charts/applications/<domain>/<app>/values.yaml`

**Purpose:**

- App-specific default configuration
- Override via cluster values files
- Document available configuration options

**What to Customize:**

```yaml
# charts/applications/ai/ollama/values.yaml

# Image configuration
image:
  repository: docker.io/ollama/ollama
  tag: "0.1.17"
  pullPolicy: IfNotPresent

# Resource requests (topology-aware)
resources:
  requests:
    memory: '{{ .Values.topology.resources.ai.memory | default "2Gi" }}'
    cpu: '{{ .Values.topology.resources.ai.cpu | default "500m" }}'

# Persistence
persistence:
  enabled: true
  size: '{{ .Values.topology.storage.ai | default "50Gi" }}'
  storageClass: "" # Use cluster default

# Route configuration
route:
  enabled: true
  host: "ollama.apps.{{ .Values.cluster.name }}.{{ .Values.cluster.top_level_domain }}"
```

**Best Practices:**

- Provide sensible defaults
- Document all values in comments
- Use topology-aware values where appropriate
- Reference cluster values via `.Values.cluster.*`
- Include examples for common configurations

---

### 🔧 Extension Files (EXTEND AS NEEDED)

These files can be added to extend functionality without modifying framework.

#### Custom Application Charts

**Location:** `charts/applications/<domain>/<your-app>/`

**Purpose:**

- Add new applications not in framework
- Domain-specific customizations
- Internal/proprietary applications

**How to Create:**

```bash
# Use scaffolding script
./scripts/chart-tools/scaffold-new-chart.sh <domain> <app-name>

# Or manually create structure:
charts/applications/<domain>/<your-app>/
├── Chart.yaml
├── values.yaml
├── README.md
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── route.yaml
│   └── NOTES.txt
└── crds/ (if needed)
```

**Best Practices:**

- Follow [Chart Standards](./CHART-STANDARDS.md)
- Use audit tool to validate
- Add to values files (commented by default)
- Document in chart README
- Add to cleanup script

#### Custom Platform Components

**Location:** `charts/platform/<your-component>/`

**Purpose:**

- Add platform-level capabilities
- Cluster-wide operators
- Infrastructure services

**Examples:**

- Custom operators
- Monitoring stack
- Security tooling
- Backup solutions

**Best Practices:**

- Namespace-scoped when possible
- Use sync-wave annotations appropriately
- Document operator maturity level
- Include CRDs in `crds/` directory

#### Custom Scripts

**Location:** `scripts/custom/` (create if needed)

**Purpose:**

- Automation specific to your deployment
- Integration scripts
- Reporting tools
- Maintenance tasks

**Best Practices:**

- Document in script README
- Make scripts idempotent
- Include error handling
- Add to Taskfile if appropriate

#### Custom Documentation

**Location:** `docs/custom/` (create if needed)

**Purpose:**

- Organization-specific procedures
- Environment details
- Runbooks
- Playbooks

**Best Practices:**

- Link from main INDEX.md
- Follow documentation standards
- Keep up to date with changes

---

## 🎨 Customization Patterns

### Pattern 1: Enable/Disable Applications

**Correct Way:**

```yaml
# clusters/individual-clusters/values-sno.yaml
clusterGroup:
  applicationStacks:
    ai:
      enabled: true
      apps:
        - ollama # Enabled
        # - litellm   # Disabled
```

**Incorrect Way:**

❌ Deleting ApplicationSet template
❌ Modifying ApplicationSet generators
❌ Commenting out template sections

### Pattern 2: Override Application Configuration

**Correct Way:**

```yaml
# clusters/individual-clusters/values-sno.yaml
clusterGroup:
  applicationStacks:
    ai:
      ollama:
        image:
          tag: "0.1.18" # Override version
        resources:
          requests:
            memory: "4Gi" # Override resources
```

**Chart must support:**

```yaml
# charts/applications/ai/ollama/values.yaml
image:
  tag: '{{ .Values.config.ollama.image.tag | default "0.1.17" }}'

resources:
  requests:
    memory: '{{ .Values.config.ollama.resources.requests.memory | default "2Gi" }}'
```

### Pattern 3: Add Cluster-Specific Storage

**Correct Way:**

```yaml
# clusters/individual-clusters/values-sno.yaml
clusterGroup:
  storage:
    truenas:
      enabled: true
      apiUrl: "https://truenas.sno.example.com"
    synology:
      enabled: false # Not used on this cluster
```

**Incorrect Way:**

❌ Modifying storage chart templates
❌ Hardcoding cluster name in charts
❌ Creating cluster-specific storage charts

### Pattern 4: Topology-Specific Sizing

**Correct Way:**

```yaml
# roles/sno/values.yaml (Framework file - don't modify)
topology:
  type: sno
  replicas:
    default: 1
  pdb:
    enabled: false

# Application chart uses topology (no modification needed)
spec:
  replicas: { { .Values.topology.replicas.default } }
```

**If Override Needed:**

```yaml
# clusters/individual-clusters/values-sno.yaml
clusterGroup:
  applicationStacks:
    media:
      plex:
        replicas: 1 # Override topology default if needed
```

---

## ⚠️ Common Pitfalls

### 1. Modifying Role Templates

**Problem:**

```bash
# Editing this file directly
vim roles/sno/templates/ai-applicationset.yaml
```

**Why Bad:**

- Will be overwritten by `sync-role-templates.sh`
- Breaks consistency across roles
- Makes framework updates difficult

**Correct Approach:**

```yaml
# Edit cluster values instead
# clusters/individual-clusters/values-sno.yaml
clusterGroup:
  applicationStacks:
    ai:
      enabled: true
      apps:
        - ollama
```

### 2. Hardcoding Cluster Names

**Problem:**

```yaml
# charts/applications/ai/ollama/templates/route.yaml
spec:
  host: ollama.apps.sno.example.com # Hardcoded!
```

**Why Bad:**

- Doesn't work on other clusters
- Can't be overridden
- Breaks portability

**Correct Approach:**

```yaml
spec:
  host: '{{ include "app.name" . }}.apps.{{ .Values.cluster.name }}.{{ .Values.cluster.top_level_domain }}'
```

### 3. Embedding Secrets in Values

**Problem:**

```yaml
# values-sno.yaml (committed to Git)
clusterGroup:
  storage:
    truenas:
      apiKey: "1-xxxxxxxxxxxxxxxxxxxxxx" # Secret in Git!
```

**Why Bad:**

- Secrets exposed in version control
- Security risk
- Difficult to rotate

**Correct Approach:**

```yaml
# Use external-secrets-operator
# charts/applications/.../templates/externalsecret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: truenas-api-key
spec:
  secretStoreRef:
    name: vault-backend
  target:
    name: truenas-credentials
  data:
    - secretKey: apiKey
      remoteRef:
        key: truenas/api-key
```

### 4. Modifying CRDs

**Problem:**

```bash
# Editing CRD directly
vim charts/platform/metallb/crds/metallb-crds.yaml
```

**Why Bad:**

- Vendor-provided definitions
- Breaks upgrades
- May cause API incompatibility

**Correct Approach:**

- Submit upstream PR for CRD changes
- Use custom resources (CRs) to configure
- Contact vendor for support

---

## 📋 Quick Reference

### What Can I Modify?

| File/Directory                               | Modify?    | Purpose                                      |
| -------------------------------------------- | ---------- | -------------------------------------------- |
| `clusters/individual-clusters/values-*.yaml` | ✅ YES     | Cluster configuration                        |
| `clusters/sets/values-*.yaml`                | ✅ YES     | Cluster set configuration                    |
| `clusters/topologies/values-*.yaml`          | ⚠️ CAREFUL | Topology defaults (usually don't need to)    |
| `values-global.yaml`                         | ⚠️ CAREFUL | Pattern-wide defaults (rarely modify)        |
| `values-secret.yaml`                         | ✅ YES     | Local secrets (git-ignored)                  |
| `roles/*/templates/`                         | ❌ NO      | Framework ApplicationSet deployers           |
| `roles/*/values.yaml`                        | ⚠️ CAREFUL | Topology defaults (usually don't need to)    |
| `charts/applications/*/values.yaml`          | ✅ YES     | App defaults (or override in cluster values) |
| `charts/applications/*/templates/`           | ⚠️ CAREFUL | Only if adding features/fixes                |
| `charts/platform/*/templates/`               | ⚠️ CAREFUL | Only if adding features/fixes                |
| `charts/*/crds/`                             | ❌ NO      | Vendor-provided CRDs                         |
| Custom charts (new apps)                     | ✅ YES     | Your applications                            |
| `scripts/custom/`                            | ✅ YES     | Your automation                              |
| `docs/custom/`                               | ✅ YES     | Your documentation                           |

### Before Modifying Framework Files

Ask yourself:

1. **Can I achieve this via values files?** (Usually yes)
2. **Does this affect all clusters?** (Probably should use values)
3. **Will this break on framework updates?** (Likely if modifying templates)
4. **Is this a contribution to the framework?** (Then PR to upstream)

If you must modify framework files:

- [ ] Document why in `docs/CHART-EXCEPTIONS.md`
- [ ] Review [ADRs](./decisions/) for alignment
- [ ] Consider contributing upstream
- [ ] Document in commit message
- [ ] Update related documentation

---

## 🔗 Related Documentation

- [Values Hierarchy](./VALUES-HIERARCHY.md) - Configuration precedence
- [Chart Standards](./CHART-STANDARDS.md) - Chart development standards
- [Change Management](./CHANGE-MANAGEMENT.md) - Making changes safely
- [Known Gaps](./KNOWN-GAPS.md) - Current limitations
- [Documentation Index](./INDEX.md) - All documentation

---

**Last Updated:** 2025-11-07
**Maintained By:** Repository maintainers
**Feedback:** Open an issue to suggest improvements
