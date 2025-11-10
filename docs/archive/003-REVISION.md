# ADR 003 Revision: Align with Actual Requirements

**Date:** 2025-11-06
**Based on:** User's detailed decision tree and current implementation review

## Critical Findings

### What I Got Wrong in Original ADR 003

1. **Misunderstood the hierarchy** - The multi-layer approach (cluster-set → topology → cluster) is CORRECT and working
2. **Oversimplified** - Suggested collapsing layers when they serve different purposes
3. **Missed cluster-set importance** - Home/WorkLab/Cloud differentiation is critical for platform config

### What's Actually Right

The current `values-global.yaml` → `values-{home|worklab|cloud}.yaml` → `values-{sno|compact|full}.yaml` → `values-{cluster}.yaml` hierarchy **WORKS** and maps to your decision tree perfectly.

## Revised Recommendations

### ✅ KEEP (High Value)

1. **Multi-layer values hierarchy**

   ```
   values-global.yaml           # Pattern defaults
   ├── values-home.yaml         # Home: TrueNAS + Cloudflare + Infisical + Keepalived
   ├── values-worklab.yaml      # Work: No TrueNAS + Different certs + Different secrets
   └── values-cloud.yaml        # Cloud: Cloud-native services
       ├── values-sno.yaml      # Topology: 1 replica
       ├── values-compact.yaml  # Topology: 2-3 replicas + PDBs
       └── values-full.yaml     # Topology: 3+ replicas + full PDBs
           └── values-{cluster}.yaml  # Specific cluster config
   ```

2. **Cluster Set Concept** - Critical for:

   - Storage provider selection (TrueNAS vs ODF vs cloud)
   - Certificate provider (Cloudflare vs Route53 vs Azure DNS vs internal CA)
   - Secret backend (Infisical vs Vault vs AWS Secrets vs Azure Key Vault)
   - Network config (Keepalived for home, different for work/cloud)

3. **Topology Files** - Provide real value:

   - `values-sno.yaml` - Single replica, minimal resources
   - `values-compact.yaml` - 2-3 replicas, PDBs for maintenance
   - `values-full.yaml` - Standard replicas, full PDBs

4. **Roles Structure** - Minimal overhead, provides Helm release context

### 🗑️ DELETE (Zero Value)

1. **`charts/topology/` directories** - All empty, no code references
   ```bash
   rm -rf charts/topology/sno/
   rm -rf charts/topology/compact/
   rm -rf charts/topology/full/
   rmdir charts/topology/
   ```

### 🔧 FIX (Name Collision)

**Problem:** `values-sno.yaml` is used both as:

- Topology file (replica counts for SNO topology)
- Cluster name (production media cluster)

**Solution Options:**

**Option A: Rename Production Cluster (Recommended)**

```bash
git mv values-sno.yaml values-sno-production.yaml
# Keep values-sno.yaml as pure topology
```

**Option B: Keep Current (Document Clearly)**

- Accept dual purpose for production cluster
- Document in VALUES-HIERARCHY.md

### 🚀 ENHANCE (Future Improvements)

#### 1. Make Platform Components Cluster-Set Aware

**Certificates Chart**

```yaml
# charts/platform/certificates/values.yaml
certificates:
  # Provider selection based on cluster set
  providers:
    cloudflare:
      enabled: '{{ eq .Values.clusterSet.name "home" }}'
      apiTokenSecret: cloudflare-api-token

    route53:
      enabled: '{{ eq .Values.clusterSet.name "cloud" }}'
      region: "{{ .Values.cloud.region }}"

    azureDns:
      enabled: '{{ and (eq .Values.clusterSet.name "cloud") (eq .Values.cloud.provider "azure") }}'

    custom:
      enabled: '{{ eq .Values.clusterSet.name "worklab" }}'
      acmeServer: https://acme.corp.example.com
```

**External Secrets Operator Chart**

```yaml
# charts/platform/external-secrets-operator/templates/cluster-secret-store.yaml
{{- if eq .Values.clusterSet.name "home" }}
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: infisical
spec:
  provider:
    infisical:
      serverURL: {{ .Values.externalSecrets.infisical.serverUrl }}
{{- else if eq .Values.clusterSet.name "worklab" }}
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault
spec:
  provider:
    vault:
      server: {{ .Values.externalSecrets.vault.vaultUrl }}
{{- else if eq .Values.clusterSet.name "cloud" }}
# Cloud-specific secret store (AWS, Azure, GCP)
{{- end }}
```

#### 2. Enable Per-App Cluster/Namespace Configuration

```yaml
# values-test.yaml (cluster-specific app overrides)
applicationStacks:
  media:
    enabled: true
    apps:
      plex:
        enabled: true
        replicas: 1 # Override topology default
        resources:
          limits:
            memory: 4Gi
          requests:
            memory: 2Gi
        persistence:
          config:
            size: 10Gi # Smaller for test
```

#### 3. Multi-Hub Support (Future)

```yaml
# values-home.yaml
clusterSet:
  name: home
  hubs:
    - name: hub1
      location: datacenter1
      managedClusters:
        - sno-production
        - test
    - name: hub2 # Future: blast radius reduction
      location: datacenter2
      managedClusters:
        - sno-backup
```

#### 4. Multi-Repo Pattern Support (Stretch Goal)

```yaml
# values-global.yaml
repoStructure:
  pattern: mono # mono | platform-apps | platform-apps-per-domain | platform-apps-per-app

  deployment:
    method: direct # direct | acm

  platformRepo:
    url: https://github.com/rbales79/argo-apps
    path: charts/platform
    targetRevision: HEAD

  appsRepo:
    url: https://github.com/rbales79/argo-apps # Same for mono-repo
    path: charts/applications
    targetRevision: HEAD
```

## Corrected Decision Tree Mapping

### Your Requirements → Implementation

```
Cluster Set (Environment)
├── Home (PRIMARY - TrueNAS, Cloudflare, Infisical, Keepalived)
│   │
│   ├── Hub (ACM/MCE, Compact topology)
│   │   └── values-hub.yaml
│   │
│   ├── Test (Dev/Test, SNO topology, -Keepalived -Kasten +MetalLB +Paperless)
│   │   └── values-test.yaml
│   │
│   └── SNO Production (Media, SNO topology, ALL components)
│       └── values-sno-production.yaml (currently values-sno.yaml)
│
├── Work Lab (SECONDARY - No TrueNAS, different certs, different secrets)
│   │
│   ├── Compact Cluster
│   │   └── values-worklab-compact1.yaml
│   │
│   └── Full HA Cluster
│       └── values-worklab-full1.yaml
│
└── Cloud (STRETCH GOAL - Cloud-native services)
    │
    ├── ROSA (AWS)
    │   └── values-rosa-prod.yaml
    │
    ├── ARO (Azure)
    │   └── values-aro-prod.yaml
    │
    ├── IBM Cloud (TechZone / Partner Demo)
    │   └── values-ibm-prod.yaml
    │
    └── OpenShift (generic cloud)
        └── values-cloud-generic.yaml
```

### File Loading Order

**Home - SNO Production (Media):**

```bash
helm install sno ./roles/sno \
  -f values-global.yaml \      # Pattern defaults
  -f values-home.yaml \         # Home lab (TrueNAS, Cloudflare, Infisical)
  -f values-sno.yaml \          # SNO topology (1 replica, minimal)
  -f values-sno-production.yaml # Cluster-specific (apps, IPs)
```

**Home - Test Cluster:**

```bash
helm install test ./roles/test \
  -f values-global.yaml \
  -f values-home.yaml \         # Home lab base
  -f values-sno.yaml \          # SNO topology
  -f values-test.yaml           # Test-specific (-Keepalived +MetalLB +Paperless)
```

**Work Lab - Compact:**

```bash
helm install worklab-compact1 ./roles/compact \
  -f values-global.yaml \
  -f values-worklab.yaml \      # Work lab (no TrueNAS, different certs)
  -f values-compact.yaml \      # Compact topology (2-3 replicas, PDBs)
  -f values-worklab-compact1.yaml
```

## Action Items

### Immediate (Phase 1)

- [ ] Delete `charts/topology/` directories (all empty)
- [ ] Update `.github/copilot-instructions.md` with correct hierarchy
- [ ] Update `docs/VALUES-HIERARCHY.md` with accurate examples
- [ ] Add cluster-set awareness note to ADR 002

### Short-term (Phase 2)

- [ ] Decide on SNO name collision fix (rename or document)
- [ ] Add cluster-set validation to platform charts
- [ ] Document certificate provider options per cluster-set
- [ ] Document ESO backend options per cluster-set

### Medium-term (Phase 3)

- [ ] Implement cluster-set aware certificate selection
- [ ] Implement cluster-set aware ESO backend selection
- [ ] Add per-app cluster/namespace configuration examples
- [ ] Test work lab deployment with different cert provider

### Long-term (Phase 4)

- [ ] Design multi-hub architecture
- [ ] Design multi-repo pattern support
- [ ] Implement ACM-based deployment option
- [ ] Add cloud provider specific configurations

## Consequences

### Positive

- ✅ Aligns with actual working implementation
- ✅ Supports all three cluster sets (home, worklab, cloud)
- ✅ Enables environment-specific platform configuration
- ✅ Maintains topology benefits (replica counts per node count)
- ✅ Provides clear path for future enhancements

### Negative

- ❌ More complex than original ADR 003 proposal
- ❌ Requires understanding 4-layer hierarchy
- ❌ Name collision with SNO needs resolution

### Neutral

- ⚪ Still deletes unused `charts/topology/` directories
- ⚪ Keeps values file count the same
- ⚪ Maintains roles structure

## Lessons Learned

1. **Don't oversimplify** - Multi-layer hierarchy exists for good reasons
2. **Cluster-set matters** - Environment (home/work/cloud) drives platform decisions
3. **Topology matters** - Node count drives replica/resource decisions
4. **Both layers needed** - Can't collapse without losing flexibility
5. **Empty directories don't justify** - Delete `charts/topology/` but keep values files

## References

- Original ADR 003 (this document supersedes sections of it)
- `docs/VALUES-HIERARCHY.md` - Current implementation (correct)
- User decision tree (source of truth)
- Current values files (working implementation)
