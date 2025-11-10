---
status: accepted
date: 2025-11-06
decision-makers: ["Roy Bales"]
---

# ADR 003: Simplify Cluster Topology Structure

## Context

The current implementation uses a **multi-layer values hierarchy** that actually works well but has one unused component:

### Current Structure (Working)

1. **`values-global.yaml`** - Pattern-wide defaults
2. **Cluster Set Layer** - Environment-specific configs:
   - `values-home.yaml` - Home lab (TrueNAS, Cloudflare, Infisical) - **PRIMARY FOCUS**
   - `values-worklab.yaml` - Work lab (no TrueNAS, different certs) - **SECONDARY**
   - `values-cloud.yaml` - Cloud providers (ROSA, ARO, IBM Cloud) - **STRETCH GOAL**
3. **Topology Layer** - Node count specific configs:
   - `values-sno.yaml` - Single Node (1 replica, minimal resources)
   - `values-compact.yaml` - 3-node (2-3 replicas, PDBs for maintenance)
   - `values-full.yaml` - 6+ nodes (standard replicas, full PDBs)
4. **Cluster-Specific** - Individual cluster configs:
   - `values-hub.yaml`, `values-test.yaml`, `values-sno.yaml` (reuses SNO topology name)
5. **`roles/<cluster>/`** - Helm charts that deploy ApplicationSets (4 roles: sno, hub, test, template)
6. **`charts/topology/<type>/`** - **EMPTY DIRECTORIES** (sno, compact, full - all unused)

### The Real Decision Tree

**Cluster Set** (environment) → **Topology** (node count) → **Cluster** (specific instance)

Examples:

- Home → SNO → test cluster: `global + home + sno + test`
- Home → SNO → production media: `global + home + sno + sno` (name collision)
- Home → Compact → hub: `global + home + compact + hub`
- Work Lab → Compact → cluster: `global + worklab + compact + worklab-compact1`

### Current Issues

1. **Empty Directory Structure:** `charts/topology/` directories are all empty - no value delivered
2. **Name Collision:** `values-sno.yaml` used both as topology AND as cluster name (production media)
3. **Topology vs Cluster Confusion:** Unclear when to use topology file vs cluster file
4. **Missing Flexibility:** Topology files don't account for environment differences (Home needs TrueNAS, Work Lab doesn't)
5. **Certificate/ESO Variability:** Home uses Cloudflare+Infisical, Work Lab needs different providers, Cloud uses cloud-native

### What's Working

- ✅ Master ApplicationSets (platform, ai, media, etc.) eliminate duplication
- ✅ Values hierarchy (`values-global.yaml` → `values-<cluster>.yaml`) works well
- ✅ Application domain organization (ai, media, home-automation, etc.) is clear
- ✅ Platform components in `charts/platform/` provide good separation

## Decision

**Keep the working multi-layer values hierarchy but delete the unused `charts/topology/` directories and clarify topology vs cluster naming.**

### Proposed Structure

```text
# Values Hierarchy (KEEP - This works!)
values-global.yaml                      # Pattern defaults
├── values-home.yaml                    # Home lab cluster set (TrueNAS, Cloudflare, Infisical)
│   ├── values-sno.yaml                 # SNO topology (1 replica, minimal)
│   │   ├── values-sno-production.yaml  # RENAMED: Production media cluster
│   │   └── values-test.yaml            # Test/dev cluster
│   └── values-hub.yaml                 # Hub cluster (compact topology inline)
├── values-worklab.yaml                 # Work lab cluster set (no TrueNAS, different certs)
│   ├── values-compact.yaml             # Compact topology (2-3 replicas, PDBs)
│   │   └── values-worklab-compact1.yaml
│   └── values-full.yaml                # Full HA topology (3+ replicas)
│       └── values-worklab-full1.yaml
└── values-cloud.yaml                   # Cloud cluster set (ROSA, ARO, IBM Cloud)
    ├── values-compact.yaml             # Shared topology
    └── values-rosa-prod.yaml           # Specific cloud cluster

# Roles (KEEP - Minimal, provides value)
roles/
  ├── sno/              # Deploys ApplicationSets for SNO clusters
  ├── hub/              # Deploys ApplicationSets for hub cluster
  ├── test/             # Deploys ApplicationSets for test cluster
  ├── compact/          # NEW: Deploys ApplicationSets for compact clusters
  ├── full/             # NEW: Deploys ApplicationSets for full HA clusters
  └── template/         # Reference template

# Charts (KEEP platform & apps, DELETE topology)
charts/
  ├── platform/         # Platform components with cluster-set awareness
  │   ├── certificates/ # Supports Cloudflare, AWS Route53, Azure DNS, etc.
  │   ├── external-secrets-operator/  # Supports Infisical, Vault, AWS Secrets, etc.
  │   └── ...
  ├── applications/     # User workloads with namespace/cluster config options
  └── [DELETE topology/]  # Empty directories provide no value
```

### Rationale

1. **Multi-Layer Hierarchy Works**

   - Cluster Set (home/worklab/cloud) → Topology (sno/compact/full) → Cluster (specific instance)
   - Matches your decision tree: environment determines platform config, topology determines replicas
   - Each layer has a clear purpose

2. **Cluster Set = Platform Configuration**

   - **Home:** TrueNAS + Cloudflare + Infisical + Keepalived + AMD GPU
   - **Work Lab:** No TrueNAS + Different cert provider + Different secret backend
   - **Cloud:** Cloud-managed storage + Cloud DNS + Cloud secrets
   - ESO and Certificates need cluster-set-specific configuration

3. **Topology = Replica Counts & Resources**

   - **SNO:** Single replica, minimal resources, no PDBs
   - **Compact:** 2-3 replicas, PDBs allowing maintenance, still small
   - **Full:** Standard replicas, full PDBs, standard resources
   - Apps may need namespace-specific overrides within topology

4. **Fix Name Collision**

   - Current: `values-sno.yaml` is both topology AND cluster name
   - Proposed: Rename production cluster to `values-sno-production.yaml`
   - Keep `values-sno.yaml` as pure topology (replica counts only)

5. **Charts/Topology Provides No Value**
   - All three directories completely empty
   - Topology config belongs in values files, not chart directories
   - Can delete without breaking anything

## Implementation Plan

### Phase 1: Cleanup (Immediate)

1. **Delete Empty Topology Directories:**

   ```bash
   rm -rf charts/topology/sno/
   rm -rf charts/topology/compact/
   rm -rf charts/topology/full/
   rmdir charts/topology/  # Should be empty
   ```

2. **Update Documentation:**

   - Remove topology references from copilot-instructions.md
   - Update ADR 002 to reflect topology deletion
   - Simplify adding-application.md workflow

3. **Verify No Dependencies:**
   - Grep for "charts/topology" references
   - Ensure no ApplicationSets reference topology paths

### Phase 2: Consolidation (Optional Future)

Consider consolidating `values-compact.yaml` and `values-full.yaml`:

**Option A: Delete Unused Files**

- If compact/full topologies aren't being used, delete the values files
- Keep only cluster-specific values (sno, hub, test, home, worklab, cloud)

**Option B: Rename to Cluster Names**

- If compact/full represent actual clusters, rename them:
  - `values-compact.yaml` → `values-<actual-cluster-name>.yaml`
  - `values-full.yaml` → `values-<actual-cluster-name>.yaml`

**Option C: Keep as Templates**

- Rename to make purpose clear:
  - `values-compact.yaml` → `values-template-3node.yaml`
  - `values-full.yaml` → `values-template-ha.yaml`

### Phase 3: Simplify Roles (Future Enhancement)

Investigate if roles can be simplified further:

**Current State:**

```
roles/sno/
  ├── Chart.yaml          # Minimal chart metadata
  ├── templates/
  │   ├── platform-applicationset.yaml
  │   ├── ai-applicationset.yaml
  │   ├── media-applicationset.yaml
  │   └── ... (6-8 ApplicationSet deployers)
  └── values.yaml         # Empty or minimal
```

**Question:** Can we eliminate roles entirely and use Argo CD App-of-Apps pattern?

Pros:

- One less directory structure
- Pure GitOps - everything in values files
- Clearer for beginners

Cons:

- Validated Patterns uses Helm + ApplicationSets
- Role provides cluster-scoped Helm release name
- Breaking change for existing deployments

**Recommendation:** Keep roles for now - they're minimal and provide value.

## Decision Matrix

### What to Keep

| Component               | Keep?  | Reason                                 |
| ----------------------- | ------ | -------------------------------------- |
| `values-global.yaml`    | ✅ Yes | Pattern-wide defaults                  |
| `values-<cluster>.yaml` | ✅ Yes | Per-cluster config (core concept)      |
| `roles/<cluster>/`      | ✅ Yes | Minimal, provides Helm release context |
| `charts/platform/`      | ✅ Yes | Platform component separation          |
| `charts/applications/`  | ✅ Yes | User workload organization             |

### What to Remove

| Component             | Remove?  | Reason                                     |
| --------------------- | -------- | ------------------------------------------ |
| `charts/topology/`    | ✅ Yes   | Empty, no value, adds complexity           |
| `values-compact.yaml` | ⚠️ Maybe | If unused or rename to actual cluster name |
| `values-full.yaml`    | ⚠️ Maybe | If unused or rename to actual cluster name |

## Consequences

### Positive

1. **Reduced Complexity:** Two config points instead of three
2. **Clearer Mental Model:** Cluster = unique config, not topology = config
3. **Easier Troubleshooting:** Less directory traversal
4. **Better Alignment with Reality:** We don't actually deploy by topology
5. **Simplified Onboarding:** New users/agents have fewer concepts to learn
6. **ADR Consistency:** Removes unused structure from ADR 002

### Negative

1. **Deviation from Validated Patterns:** Standard patterns include topology layer
2. **Future-Proofing:** If we want ODF later, need to add it to platform or create new structure
3. **Migration Effort:** Need to update docs and potentially regenerate files

### Neutral

1. **Storage Strategy:** Doesn't change - TrueNAS remains default
2. **Application Deployment:** Doesn't change - still using ApplicationSets
3. **Values Hierarchy:** Doesn't change - still inherits from global

## Examples

### Before (Current - Complex)

Adding a new cluster requires:

1. Create `values-newcluster.yaml` (cluster config)
2. Create `roles/newcluster/` (ApplicationSet deployers)
3. Create `charts/topology/newcluster/`? (unclear if needed)
4. Understand topology vs cluster distinction

### After (Proposed - Simple)

Adding a new cluster requires:

1. Create `values-newcluster.yaml` (cluster config)
2. Copy `roles/template/` to `roles/newcluster/` (ApplicationSet deployers)
3. Done! Clear path forward.

## Migration Checklist

- [ ] Delete `charts/topology/sno/`
- [ ] Delete `charts/topology/compact/`
- [ ] Delete `charts/topology/full/`
- [ ] Delete `charts/topology/` (parent directory)
- [ ] Grep for "topology" references in codebase
- [ ] Update `.github/copilot-instructions.md` (remove topology mentions)
- [ ] Update ADR 002 (add note about topology deletion)
- [ ] Update `docs/CHART-STANDARDS.md` if needed
- [ ] Update `scripts/README.md` if needed
- [ ] Test deployments on test cluster
- [ ] Verify no ApplicationSets reference topology paths
- [ ] Update this ADR status to "Accepted" when complete

## Alternative Considered: Keep Topology for Future ODF

**Alternative:** Keep `charts/topology/` for future ODF deployment on compact/full clusters.

**Rejected Because:**

1. ODF can be added to `charts/platform/` with feature flag when needed
2. Empty directories add cognitive load with zero current value
3. Storage strategy is unified (TrueNAS) - no evidence of future ODF need
4. Easier to add back later if truly needed than to maintain unused structure

## References

- [ADR 002: Validated Patterns Framework Migration](./002-validated-patterns-framework-migration.md)
- [Validated Patterns OpenShift Framework](https://validatedpatterns.io/learn/vp_openshift_framework/)
- [YAGNI Principle](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it)

## Notes

- **Validated Patterns Compliance:** This deviates from the standard pattern but aligns with YAGNI
- **Cluster vs Topology:** A cluster name (sno, hub, test) is more specific than a topology type (sno, compact, full)
- **Future Evolution:** If ODF needed, add to `charts/platform/` with `clusterGroup.storage.odf.enabled: true`
- **Template Pattern:** Keep `roles/template/` as reference for new clusters
