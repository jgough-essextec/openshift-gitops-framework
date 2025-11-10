---
status: accepted
date: 2024-11-05
decision-makers: ["Roy Bales"]
---

# ADR 002: Validated Patterns Framework Migration

## Context

The existing argo-apps repository used a flat chart structure organized by functional domain (ai/, media/, base/, etc.) with ApplicationSets in each cluster role managing apps individually. As the number of applications and clusters grew, this approach created several challenges:

1. **Duplication:** ApplicationSet templates were duplicated across cluster roles (sno, hub, test)
2. **Complexity:** No clear separation between infrastructure components, topology-specific configs, and user applications
3. **Scalability:** Difficult to add new cluster types or topologies without extensive duplication
4. **Values Management:** Cluster-specific configuration spread across multiple ApplicationSets with no clear hierarchy

## Decision

Adopt the **Validated Patterns Framework** structure with a three-layer architecture:

### Layer 1: Platform Components (`charts/platform/`)

Components that deploy conditionally per cluster (22 total charts):

**Core Platform Services (enabled by default):**

- external-secrets-operator (secrets management)
- cert-manager (certificates)
- openshift-nfd (Node Feature Discovery)
- vertical-pod-autoscaler (VPA)
- gatus (health monitoring)
- goldilocks (resource recommendations)
- custom-error-pages (branded error pages)
- generic-device-plugin (hardware access)
- argocd-resource-config (GitOps configuration)
- snapshot-finalizer-remover (cleanup jobs)

**Storage Providers:**

- truenas (CSI storage provider) - default storage for all clusters
- synology (CSI storage provider) - alternative storage option

**Networking:**

- metallb (load balancer) - disabled by default, using native OpenShift networking

**Multi-cluster Management (moved from region for DRY):**

- advanced-cluster-management (ACM) - enable on hub cluster(s)
- multicluster-engine (MCE) - enable on hub cluster(s)

**Hardware Support (optional per cluster):**

- amd-gpu-operator (AMD GPU support)
- intel-gpu-operator (Intel GPU support)

**Backup & HA (optional per cluster):**

- k10-kasten-operator (Veeam Kasten backup)
- keepalived-operator (VRRP HA)

**Cluster Tweaks:**

- disable-master-secondary-interfaces
- disable-worker-secondary-interfaces

### Layer 2: Regional Components (`charts/region/`)

**DELETED** - ACM/MCE moved to platform layer for DRY principle (can be on any cluster, not just hub)

### Layer 3: Topology-Specific (`charts/topology/`)

Alternative storage providers specific to cluster topology (TrueNAS is default in platform layer):

- **sno/** - Single Node OpenShift:
  - (empty - uses platform TrueNAS)
- **compact/** - 3-node clusters:
  - ODF (OpenShift Data Foundation - optional alternative to TrueNAS)
- **full/** - 6+ node HA clusters:
  - ODF (OpenShift Data Foundation - optional alternative to TrueNAS)

### Layer 4: User Applications (`charts/applications/`)

User workloads organized by domain:

- **ai/** - AI/ML applications (litellm, ollama, open-webui)
- **media/** - Media management (plex, sonarr, radarr, etc.)
- **home-automation/** - IoT/smart home (home-assistant, node-red, emqx-operator, zwavejs2mqtt)
- **productivity/** - Productivity tools (bookmarks, cyberchef, excalidraw, it-tools, startpunkt, terraform-enterprise)
- **infrastructure/** - Special-purpose apps (paperless suite, adsb)

## Values Hierarchy

Implemented a cascading values hierarchy:

```
values-global.yaml              # Pattern-wide defaults
  ├── values-sno.yaml           # SNO topology overrides
  ├── values-compact.yaml       # Compact topology overrides
  ├── values-full.yaml          # Full HA topology overrides
  └── values-hub.yaml           # Hub cluster overrides
      └── values-secret.yaml    # Encrypted secrets
```

**Key Principles:**

- **TrueNAS CSI** is the default storage provider for all clusters
- **Topology files** can override storage (e.g., compact/full use ODF)
- **Component enablement** controlled via `clusterGroup.commonComponents`, `clusterGroup.storage`, `clusterGroup.applicationStacks`
- **Secrets** managed separately in `values-secret.yaml` (encrypted)

## Implementation Steps

### ✅ Completed (2024-11-05)

1. **Created Directory Structure:**

   ```bash
   charts/
   ├── platform/         # Platform components (20 charts including storage)
   ├── region/
   │   ├── hub/         # ACM, MCE (2 charts)
   │   ├── edge/        # (empty, future)
   │   └── datacenter/  # (empty, future)
   ├── topology/
   │   ├── sno/         # (empty - uses platform defaults)
   │   ├── compact/     # (empty - ODF to be added)
   │   └── full/        # (empty - ODF to be added)
   └── applications/
       ├── ai/          # 3 charts
       ├── media/       # 21 charts
       ├── home-automation/  # 4 charts
       ├── productivity/     # 6 charts
       └── infrastructure/   # 5 charts
   ```

2. **Created Values Files:**

   - `values-global.yaml` - Pattern defaults with TrueNAS storage
   - `values-sno.yaml` - SNO topology with MetalLB + TrueNAS
   - `values-compact.yaml` - Compact topology (future ODF)
   - `values-full.yaml` - Full HA topology (future ODF)
   - `values-hub.yaml` - Hub cluster with ACM
   - `values-secret.yaml.template` - Secrets template
   - `pattern-metadata.yaml` - Pattern identification

3. **Migrated Charts:**
   - Moved 20 base components to `charts/platform/`
   - Moved external-secrets-operator from `charts/security/` to `charts/platform/`
   - Moved storage providers to `charts/platform/` (TrueNAS default, Synology alternative)
   - Moved MetalLB to `charts/platform/` (disabled by default - using native OpenShift networking)
   - Moved ACM/MCE to `charts/platform/` (for DRY - can be on any cluster, not just hub)
   - Moved GPU operators to `charts/platform/` (optional components)
   - Moved 40 application charts to `charts/applications/{ai,media,home-automation,productivity,infrastructure}/`
   - Moved cluster tweaks (argocd-resource-config, interface disablers, snapshot cleanup) to `charts/platform/`
   - **Deleted `charts/region/` directory** - ACM/MCE now in platform layer for flexibility

### 🔄 In Progress

4. **Create Master ApplicationSets:**

   - Create `charts/platform/applicationset.yaml` for platform components
   - Create `charts/region/hub/applicationset.yaml` for hub components
   - Create `charts/topology/sno/applicationset.yaml` for SNO topology
   - Create `charts/topology/compact/applicationset.yaml` for compact topology
   - Create `charts/topology/full/applicationset.yaml` for full topology
   - Create `charts/applications/{category}/applicationset.yaml` for each application domain

5. **Update Cluster Roles:**
   - Update `roles/sno/templates/` to use new ApplicationSets
   - Update `roles/hub/templates/` to use new ApplicationSets
   - Update `roles/test/templates/` to use new ApplicationSets
   - Remove old ApplicationSet templates (ai.yaml, media.yaml, base-\*.yaml, home-automation.yaml, productivity.yaml)

### 📋 Pending

6. **Create Topology Storage Configurations (Optional):**

   - Create ODF chart for `charts/topology/compact/` (alternative to TrueNAS)
   - Create ODF chart for `charts/topology/full/` (alternative to TrueNAS)
   - Document storage provider selection logic (TrueNAS is default in platform)

7. **Testing:**

   - Deploy to test cluster first
   - Verify all common components deploy correctly
   - Verify topology-specific components deploy correctly
   - Verify application stacks deploy correctly
   - Test values override hierarchy

8. **Documentation:**
   - Update README.md with new structure
   - Update `.github/copilot-instructions.md`
   - Update `.github/instructions/adding-application.md`
   - Create migration guide for existing clusters

## Consequences

### Positive

- **Clear Separation:** Infrastructure, topology, and applications are clearly separated
- **Reusability:** Common components defined once, deployed everywhere
- **Scalability:** Easy to add new topologies or cluster types
- **Maintainability:** Values hierarchy eliminates duplication
- **Standards-Based:** Follows Red Hat Validated Patterns framework
- **Agentic-Friendly:** Clear structure enables AI agents to understand and modify deployments

### Negative

- **Migration Complexity:** Requires updating all ApplicationSets and cluster roles
- **Learning Curve:** Team needs to understand new structure and values hierarchy
- **Temporary Duplication:** Old `charts/base/` directory kept during migration
- **Breaking Change:** Existing deployments need careful migration path

### Neutral

- **Directory Depth:** More nested directories, but better organization
- **Values Management:** More values files, but clearer hierarchy
- **ApplicationSet Count:** Same total number of apps, different grouping

## Migration Path

### For Existing Clusters

1. **Branch Strategy:**

   - Development on `framework-dev` branch
   - Test on `test` cluster first
   - Merge to `main` after validation

2. **Deployment Approach:**

   - Deploy new ApplicationSets alongside old ones
   - Verify apps deploy correctly with new structure
   - Delete old ApplicationSets once validated
   - Clean up old `charts/base/` directory

3. **Rollback Plan:**
   - Keep old ApplicationSets until new ones validated
   - Old chart paths still exist during migration
   - Can revert by re-enabling old ApplicationSets

## References

- [Validated Patterns OpenShift Framework](https://validatedpatterns.io/learn/vp_openshift_framework/)
- [Helm Chart Structure Best Practices](https://helm.sh/docs/chart_best_practices/)
- [ArgoCD ApplicationSet Patterns](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/)

## Notes

- **Default Storage:** TrueNAS CSI is the default for all clusters unless overridden by topology
- **Component Selection:** All components in `charts/platform/` deploy unless explicitly disabled in topology values
- **Secret Management:** Continue using External Secrets Operator with Infisical backend
- **GPU Operators:** Optional components in `charts/platform/`, enabled per cluster via values

## Chart Count Summary

- **charts/platform/**: 20 charts (platform components including TrueNAS, Synology, MetalLB)
- **charts/region/hub/**: 2 charts (ACM, MCE)
- **charts/topology/sno/**: 0 charts (empty - uses platform defaults)
- **charts/topology/compact/**: 0 charts (empty - ODF to be added as optional alternative)
- **charts/topology/full/**: 0 charts (empty - ODF to be added as optional alternative)
- **charts/applications/ai/**: 3 charts
- **charts/applications/media/**: 21 charts
- **charts/applications/home-automation/**: 4 charts
- **charts/applications/productivity/**: 6 charts
- **charts/applications/infrastructure/**: 5 charts

**Total:** 60 application/component charts migrated (all storage providers now in platform layer)
