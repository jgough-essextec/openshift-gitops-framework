# Repository Organization Proposal

**Date:** 2025-11-06
**Status:** Proposal / Discussion
**Related:** ADR 002 (Validated Patterns Framework)

## Current State

### Current Structure

```
values-global.yaml          # Pattern-wide defaults
values-home.yaml            # Home lab cluster set
values-worklab.yaml         # Work lab cluster set
values-cloud.yaml           # Cloud cluster set
values-prod.yaml            # Production cluster (home, SNO topology)
values-hub.yaml             # Hub cluster (home, hub role)
values-test.yaml            # Test cluster (home, SNO topology)
values-compact.yaml         # Compact topology defaults
values-full.yaml            # Full HA topology defaults

roles/
  sno/                      # SNO topology deployer
  hub/                      # Hub cluster deployer
  test/                     # Test cluster deployer
  template/                 # Template for new roles

charts/
  platform/                 # Platform components (22 charts)
  applications/             # User applications
    ai/
    media/
    home-automation/
    productivity/
    infrastructure/
  topology/                 # EMPTY - candidate for deletion
    sno/
    compact/
    full/
```

### Current Platform Component Organization

In `values-prod.yaml`, platform components are organized by **function**:

```yaml
platformComponents:
  # Security & Secrets
  externalSecrets:
    enabled: true
  certManager:
    enabled: true

  # Node & Resource Management
  nfd:
    enabled: true
  vpa:
    enabled: true
  goldilocks:
    enabled: true
  systemReservation:
    enabled: false

  # Monitoring & Health
  gatus:
    enabled: true
  customErrorPages:
    enabled: true

  # Hardware & GPU
  genericDevicePlugin:
    enabled: true
  amdGpu:
    enabled: true
  intelGpu:
    enabled: false

  # Backup & HA
  kasten:
    enabled: false
  keepalived:
    enabled: false

  # Multi-cluster Management
  acm:
    enabled: false
  multiclusterEngine:
    enabled: false

  # Tweaks
  argoCdResourceConfig:
    enabled: true
  disableMasterSecondaryInterfaces:
    enabled: true
  disableWorkerSecondaryInterfaces:
    enabled: false
  snapshotFinalizerRemover:
    enabled: true
```

## Proposal Analysis

### Question 1: Reorganize Application Domains to Match Platform Layout?

**Current application domains:**

- ai/
- media/
- home-automation/
- productivity/
- infrastructure/

**Proposed alignment with platform functional groups:**

- security-secrets/
- node-resource/
- monitoring-health/
- hardware-gpu/
- backup-ha/
- storage/
- networking/

#### ✅ RECOMMENDATION: **Keep Current Application Domains**

**Rationale:**

1. **Different Purposes:**

   - **Platform components** = Infrastructure/cluster services (operators, monitoring, storage providers)
   - **Applications** = End-user workloads (Plex, Ollama, Home Assistant)

2. **Platform functional grouping is for VALUES organization:**

   - Groups related settings in values files for easier management
   - Makes it clear which components serve similar purposes
   - Does NOT need to match directory structure

3. **Application domains are user-centric:**

   - Organized by use case (AI, Media, Home Automation)
   - Teams/users understand domains better than technical layers
   - Aligns with business value streams

4. **Chart directories should match ApplicationSet generators:**
   - Current: `charts/applications/ai/` → `applicationStacks.ai.apps`
   - Changing to technical groups would break this natural mapping

**Alternative: Enhance Platform Organization**

Instead of reorganizing applications, enhance platform chart organization:

```
charts/
  platform/
    security/              # Group related platform charts
      external-secrets-operator/
      certificates/
    node-resource/
      openshift-nfd/
      vertical-pod-autoscaler/
      goldilocks/
      system-reservation/
    monitoring/
      gatus/
      custom-error-pages/
    storage/
      truenas/
      synology/
      metallb/
    hardware/
      amd-gpu-operator/
      intel-gpu-operator/
      generic-device-plugin/
    backup/
      k10-kasten-operator/
      keepalived-operator/
    multicluster/
      advanced-cluster-management/
      multicluster-engine/
    tweaks/
      argocd-resource-config/
      disable-master-secondary-interfaces/
      disable-worker-secondary-interfaces/
      snapshot-finalizer-remover/
```

**Note:** This would require updating ApplicationSet `path` references, which is a significant change. Recommend documenting the functional grouping in values files only.

---

### Question 2: Branch Strategy - Per-Site Branches vs Single Branch?

**Option A: Per-Site Branches (home, worklab, aws, azure)**

```
Branches:
  main                      # Common code, no cluster-specific values
  site/home                 # Home lab clusters
  site/worklab              # Work lab clusters
  site/aws                  # AWS clusters
  site/azure                # Azure clusters
```

**Option B: Single Branch with Values Files (CURRENT)**

```
Branch:
  framework-dev (or main)   # All code + all cluster configs

Values structure:
  values-global.yaml
  values-home.yaml + values-prod/hub/test.yaml
  values-worklab.yaml + values-cluster1/cluster2.yaml
  values-cloud.yaml + values-aws-cluster1.yaml + values-azure-cluster1.yaml
```

#### ✅ RECOMMENDATION: **Single Branch with Values Files (Current Approach)**

**Rationale:**

1. **Validated Patterns Best Practice:**

   - Framework explicitly supports multi-site/multi-cluster from single repo
   - Values hierarchy designed for this exact use case
   - Hub cluster can manage all sites from one repo

2. **Easier Maintenance:**

   - Chart updates apply to ALL sites automatically
   - No need to merge changes across branches
   - Platform component updates happen once

3. **Secret Management:**

   - Cluster-specific secrets handled by External Secrets Operator
   - Each cluster pulls secrets from its own Infisical project/vault
   - No secrets in Git regardless of branch strategy

4. **Clear Separation Already Exists:**

   ```
   values-global.yaml      # Shared by ALL clusters (chart defaults)
   values-home.yaml        # Home lab specifics (TrueNAS, Cloudflare)
   values-worklab.yaml     # Work lab specifics (different storage/certs)
   values-cloud.yaml       # Cloud specifics (managed services)
   values-<cluster>.yaml   # Individual cluster config
   ```

5. **ArgoCD Application Source:**
   Each cluster's bootstrap Application points to:
   - Same repo
   - Same branch (main or framework-dev)
   - Different valueFiles combination

**When Per-Site Branches Make Sense:**

- **Regulatory compliance** - Different sites have different compliance requirements
- **Air-gapped environments** - Sites have no network connectivity to each other
- **Different development teams** - Teams want independent release cycles
- **Experimental features** - Testing changes without affecting other sites

**For your use case (home lab + work lab + cloud):**

- Same owner/team
- Centralized management from hub cluster
- Shared platform components
- → **Single branch is optimal**

---

## Recommended Repository Organization

### Proposed Structure

```
Repository: argo-apps
Branch: main (or framework-dev)

├── values-global.yaml              # Pattern defaults (ALL clusters)
│
├── Cluster Set Values:
│   ├── values-home.yaml            # Home lab defaults
│   ├── values-worklab.yaml         # Work lab defaults
│   └── values-cloud.yaml           # Cloud defaults
│
├── Cluster-Specific Values:
│   ├── Home Lab:
│   │   ├── values-prod.yaml        # Production (SNO)
│   │   ├── values-hub.yaml         # Hub cluster
│   │   └── values-test.yaml        # Test/dev (SNO)
│   ├── Work Lab:
│   │   ├── values-worklab-compact1.yaml
│   │   └── values-worklab-compact2.yaml
│   └── Cloud:
│       ├── values-aws-cluster1.yaml
│       └── values-azure-cluster1.yaml
│
├── Topology Defaults (for reference):
│   ├── values-compact.yaml         # 3-node defaults
│   └── values-full.yaml            # 6+ node defaults
│
├── roles/                          # Deployment bootstraps
│   ├── sno/                        # SNO clusters
│   ├── compact/                    # Compact clusters
│   ├── full/                       # Full HA clusters
│   ├── hub/                        # Hub clusters (any topology)
│   ├── test/                       # Test clusters (any topology)
│   └── template/                   # Template for new roles
│
└── charts/
    ├── platform/                   # 22 platform components
    │   ├── (current flat structure OR grouped subdirs)
    │   └── templates/
    │       └── applicationset.yaml
    │
    └── applications/               # User workloads
        ├── ai/
        ├── media/
        ├── home-automation/
        ├── productivity/
        └── infrastructure/
```

### Values File Hierarchy Examples

#### Home Lab Production Cluster

```bash
helm install prod ./roles/sno \
  -f values-global.yaml \      # Pattern defaults
  -f values-home.yaml \         # Home lab (TrueNAS, Cloudflare, Infisical)
  -f values-prod.yaml           # Production cluster (SNO topology, enabled apps)
```

#### Work Lab Compact Cluster

```bash
helm install worklab-compact1 ./roles/compact \
  -f values-global.yaml \           # Pattern defaults
  -f values-worklab.yaml \          # Work lab (ODF, internal CA, Vault)
  -f values-worklab-compact1.yaml   # Cluster specifics
```

#### AWS ROSA Cluster

```bash
helm install aws-prod ./roles/full \
  -f values-global.yaml \       # Pattern defaults
  -f values-cloud.yaml \        # Cloud (minimal platform, managed services)
  -f values-aws-cluster1.yaml   # AWS specifics (EBS, ACM, Secrets Manager)
```

---

## Implementation Plan

### Phase 1: Clarify Current Structure (Immediate - 1 hour)

1. **Document values hierarchy in each file:**

   ```yaml
   # values-home.yaml
   # PURPOSE: Home lab cluster set defaults
   # APPLIES TO: values-prod.yaml, values-hub.yaml, values-test.yaml
   # PROVIDES: TrueNAS storage, Cloudflare DNS, Infisical secrets, Let's Encrypt certs
   ```

2. **Update copilot instructions with clear guidelines:**

   - Platform components grouped by function in VALUES only
   - Application domains stay user-centric
   - Single branch strategy for multi-site management

3. **Delete `charts/topology/` directory (currently empty):**
   ```bash
   rm -rf charts/topology/
   ```

### Phase 2: Enhance Platform Organization (Optional - 2-4 hours)

**Only if functional grouping in chart directories is strongly desired.**

1. **Reorganize platform charts into subdirectories**
2. **Update ApplicationSet paths** in `charts/platform/templates/applicationset.yaml`
3. **Update all documentation references**
4. **Test deployment on all clusters**

**Risk:** Significant refactoring, potential for breaking changes.
**Benefit:** Better organization when browsing `charts/platform/` directory.
**Recommendation:** Defer unless compelling business need.

### Phase 3: Add Work Lab Clusters (Future - when ready)

1. **Create `values-worklab.yaml`** with work lab defaults
2. **Create cluster-specific values files** (e.g., `values-worklab-compact1.yaml`)
3. **Configure External Secrets Operator** for work lab secret backend
4. **Deploy using existing roles** (compact/full as appropriate)
5. **Test platform components and applications**

### Phase 4: Add Cloud Clusters (Future - when ready)

1. **Create `values-cloud.yaml`** with cloud defaults
2. **Create provider-specific values** (AWS, Azure, IBM Cloud)
3. **Configure cloud-native integrations** (managed databases, secret managers, etc.)
4. **Deploy using existing roles** (typically full HA topology)

---

## Decision Matrix

| Aspect                          | Current                        | Proposed Change                       | Recommendation             |
| ------------------------------- | ------------------------------ | ------------------------------------- | -------------------------- |
| **Application Domains**         | User-centric (ai, media, etc.) | Technical (storage, monitoring, etc.) | ❌ Keep current            |
| **Platform Chart Organization** | Flat directory                 | Grouped subdirectories                | ⚠️ Optional, document only |
| **Branch Strategy**             | Single branch                  | Per-site branches                     | ✅ Keep single branch      |
| **Values Hierarchy**            | Global → Set → Cluster         | Same                                  | ✅ Keep current            |
| **Chart Structure**             | Validated Patterns             | Same                                  | ✅ Keep current            |

---

## Answers to Your Questions

### 1. "Create domains aligned to platform apps layout?"

**Answer:** No, keep current application domains (ai, media, home-automation, productivity, infrastructure).

**Reason:** Platform components and applications serve different purposes. Platform functional grouping is for VALUES organization (easier to read/manage), not chart directory structure. Application domains are user-centric and map naturally to business value.

### 2. "Create branch for each site (home, work lab, aws, azure)?"

**Answer:** No, use single branch with values files (current approach).

**Reason:** Validated Patterns framework explicitly supports multi-site from single repo. Values hierarchy already provides clean separation. Easier maintenance, automatic chart updates across all sites, and hub cluster can manage everything from one source.

### 3. "How to prevent site-specific info from syncing?"

**Answer:** Already solved by values file hierarchy:

- **values-global.yaml** - Shared by all sites
- **values-home.yaml** - Home lab only (not used by worklab/cloud)
- **values-worklab.yaml** - Work lab only
- **values-cloud.yaml** - Cloud only
- **values-<cluster>.yaml** - Specific cluster

Each cluster's ArgoCD Application specifies which values files to use:

```yaml
# Home lab production cluster Application
spec:
  source:
    helm:
      valueFiles:
        - ../../values-global.yaml
        - ../../values-home.yaml
        - ../../values-prod.yaml

# Work lab cluster Application
spec:
  source:
    helm:
      valueFiles:
        - ../../values-global.yaml
        - ../../values-worklab.yaml
        - ../../values-worklab-compact1.yaml
```

No site-specific information "syncs" to other sites because each cluster only loads its own values files.

---

## Recommendation Summary

### ✅ DO:

1. **Keep single branch strategy** - Multi-site support via values hierarchy
2. **Keep current application domains** - User-centric organization is correct
3. **Document functional grouping in values files** - Comment sections clearly
4. **Delete `charts/topology/` directory** - It's empty and unused
5. **Create work lab / cloud values when ready** - Framework already supports it

### ❌ DON'T:

1. **Don't reorganize application domains** - Current structure is correct for Validated Patterns
2. **Don't create per-site branches** - Adds complexity without benefit for your use case
3. **Don't reorganize platform charts** - Flat structure works, grouped subdirs add complexity

### ⚠️ OPTIONAL:

1. **Platform chart subdirectories** - Only if strong preference for browsing, requires significant refactoring

---

## Next Steps

1. **Review this proposal** and decide on approach
2. **Update copilot instructions** with final decision
3. **Document in ADR** if making significant changes
4. **Test on one cluster** before rolling out widely
5. **Update change management checklist** if reorganizing charts

## References

- ADR 002: Validated Patterns Framework Migration
- `docs/VALUES-HIERARCHY.md` - Current values structure
- `docs/DECISION-TREE.md` - Deployment decision tree
- https://validatedpatterns.io/learn/vp_openshift_framework/
