# Architecture Quick Reference

Single-page visual reference for the argo-apps GitOps architecture. For detailed information, see [Detailed Overview](../DETAILED-OVERVIEW.md).

> **📋 Strategic Decisions:** See [ADR Index](../decisions/INDEX.md) for architectural rationale.

---

## 🏗️ Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Bootstrap (Manual One-Time Setup)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Argo CD Application: "cluster"                       │  │
│  │  Source: roles/<cluster-name>/                        │  │
│  │  Values: values-global.yaml + values-<cluster>.yaml   │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: ApplicationSet Deployers (Role Chart)             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Applications that deploy ApplicationSet charts:      │  │
│  │  - platform-applicationset.yaml                       │  │
│  │  - ai-applicationset.yaml                             │  │
│  │  - media-applicationset.yaml                          │  │
│  │  - home-automation-applicationset.yaml                │  │
│  │  - productivity-applicationset.yaml                   │  │
│  │  - infrastructure-applicationset.yaml                 │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: ApplicationSets (Master Charts)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  charts/platform/templates/applicationset.yaml        │  │
│  │  charts/applications/ai/templates/applicationset.yaml │  │
│  │  charts/applications/media/templates/...              │  │
│  │  (One ApplicationSet per domain)                      │  │
│  └─────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Applications (Individual Helm Charts)             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Each enabled app gets an Application:                │  │
│  │  - charts/applications/ai/ollama/                     │  │
│  │  - charts/applications/ai/litellm/                    │  │
│  │  - charts/applications/media/plex/                    │  │
│  │  - charts/applications/media/sonarr/                  │  │
│  │  (38+ application charts)                             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** This eliminates duplication. Define ApplicationSets once, enable apps via values.

---

## ⚙️ Values Hierarchy

```
┌──────────────────────────────────────────────────────────┐
│  values-global.yaml                                      │
│  Pattern-wide defaults for all clusters                 │
│  • Default replica counts                               │
│  • Common image registries                              │
│  • Standard security contexts                           │
└──────────────────┬───────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────┐
│  clusters/sets/values-<set>.yaml                         │
│  Cluster set: home | worklab | cloud                     │
│  • Storage provider (TrueNAS vs Synology vs cloud)       │
│  • Secrets provider (Infisical vs Vault vs cloud)        │
│  • Certificate provider (Let's Encrypt vs Internal CA)   │
└──────────────────┬───────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────┐
│  clusters/topologies/values-<topology>.yaml              │
│  Topology: compact | full                                │
│  • Replica counts (2-3 vs 3+)                            │
│  • PDB settings (minAvailable: 1 vs 2)                   │
│  • Resource requests (small vs standard)                 │
└──────────────────┬───────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────┐
│  clusters/individual-clusters/values-<cluster>.yaml      │
│  Individual cluster: prod | hub | test | ...             │
│  • Cluster name and domain                               │
│  • Enabled applications list                             │
│  • Cluster-specific overrides                            │
└──────────────────────────────────────────────────────────┘
```

**Helm Merge Order:** Global → Set → Topology → Cluster (later values override earlier)

**See:** [VALUES-HIERARCHY.md](../VALUES-HIERARCHY.md) for detailed examples.

---

## 🎯 Application Enablement

Apps are enabled/disabled by simple arrays in cluster values files:

```yaml
# clusters/individual-clusters/values-prod.yaml
clusterGroup:
  applicationStacks:
    ai:
      enabled: true
      apps:
        - ollama # ← Uncommented = enabled
        - open-webui
        # - litellm    # ← Commented = disabled

    media:
      enabled: true
      apps:
        - plex
        - sonarr
        - radarr
```

**No ApplicationSet editing required!** Just add/remove app names from the list.

---

## 🗂️ Repository Structure

```
argo-apps/
├── bootstrap/                      # Manual setup instructions
│   └── README.md                   # Bootstrap guide
│
├── values-global.yaml              # Pattern defaults
├── clusters/                       # Values organization
│   ├── individual-clusters/        # Per-cluster values
│   │   ├── values-prod.yaml
│   │   ├── values-hub.yaml
│   │   └── values-test.yaml
│   ├── sets/                       # Cluster set values
│   │   ├── values-home.yaml
│   │   ├── values-worklab.yaml
│   │   └── values-cloud.yaml
│   └── topologies/                 # Topology defaults
│       ├── values-compact.yaml
│       └── values-full.yaml
│
├── roles/                          # Topology-specific roles
│   ├── sno/                        # Single Node OpenShift
│   │   ├── Chart.yaml
│   │   ├── values.yaml             # SNO defaults (1 replica, no PDB)
│   │   └── templates/              # ApplicationSet deployers
│   ├── compact/                    # 3-node cluster
│   │   └── values.yaml             # Compact defaults (2-3 replicas, PDB)
│   └── full/                       # 6+ node cluster
│       └── values.yaml             # Full defaults (3+ replicas, standard PDB)
│
├── charts/                         # Helm charts
│   ├── platform/                   # Platform ApplicationSet
│   │   └── templates/
│   │       └── applicationset.yaml # Generates platform Applications
│   │
│   └── applications/               # Application domains
│       ├── ai/                     # AI/ML domain
│       │   ├── templates/
│       │   │   └── applicationset.yaml  # AI ApplicationSet
│       │   ├── ollama/             # Individual charts
│       │   ├── litellm/
│       │   └── open-webui/
│       │
│       ├── media/                  # Media domain
│       │   ├── templates/
│       │   │   └── applicationset.yaml  # Media ApplicationSet
│       │   ├── plex/
│       │   ├── sonarr/
│       │   └── radarr/
│       │
│       ├── home-automation/        # IoT domain
│       ├── productivity/           # Productivity tools
│       └── infrastructure/         # Infrastructure apps
│
├── docs/                           # Documentation
│   ├── INDEX.md                    # Documentation index
│   ├── DETAILED-OVERVIEW.md        # Complete architecture
│   ├── VALUES-HIERARCHY.md         # Values guide
│   ├── CHART-STANDARDS.md          # Chart requirements
│   ├── decisions/                  # Architectural Decision Records
│   ├── deployment/                 # Deployment patterns
│   ├── instructions/               # How-to guides
│   └── troubleshooting/            # Problem resolution
│
└── scripts/                        # Utility scripts
    ├── sync-role-templates.sh      # Sync role templates
    ├── audit/                      # Chart compliance tools
    └── cluster-operations/         # Cluster management
```

---

## 🔄 Deployment Flow

### Initial Bootstrap

```bash
# 1. Install OpenShift GitOps operator
oc apply -f bootstrap/openshift-gitops-operator.yaml

# 2. Grant Argo CD cluster-admin
oc adm policy add-cluster-role-to-user cluster-admin \
  -z openshift-gitops-argocd-application-controller \
  -n openshift-gitops

# 3. Create bootstrap Application
oc apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster
  namespace: openshift-gitops
spec:
  source:
    repoURL: https://github.com/rbales79/argo-apps.git
    targetRevision: HEAD
    path: roles/sno
    helm:
      valueFiles:
        - ../../values-global.yaml
        - ../../clusters/sets/values-home.yaml
        - ../../clusters/individual-clusters/values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: openshift-gitops
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF
```

### What Happens Next

1. **Argo CD syncs "cluster" Application**

   - Deploys role chart (`roles/sno/`)
   - Creates ApplicationSet deployer Applications

2. **ApplicationSet Deployers sync**

   - Each deploys its ApplicationSet chart
   - Creates ApplicationSet resources in `openshift-gitops` namespace

3. **ApplicationSets generate Applications**

   - Loop over enabled apps from values
   - Create Application per enabled app
   - Set sync waves for ordering

4. **Applications deploy charts**
   - Each app chart creates Kubernetes resources
   - Namespaces, Deployments, Services, Routes, PVCs
   - Apps become available at Routes

---

## 📊 Resource Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│  Namespace: openshift-gitops                                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Application: cluster                                   │   │
│  │  (Bootstrap - manually created)                         │   │
│  └────────────┬────────────────────────────────────────────┘   │
│               │ creates                                         │
│               ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Applications: *-applicationset                         │   │
│  │  - platform-applicationset                              │   │
│  │  - ai-applicationset                                    │   │
│  │  - media-applicationset                                 │   │
│  │  (Deployer Applications - generated by role chart)      │   │
│  └────────────┬────────────────────────────────────────────┘   │
│               │ creates                                         │
│               ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ApplicationSets: <cluster>-platform, <cluster>-ai, ... │   │
│  │  (Master ApplicationSets - one per domain)              │   │
│  └────────────┬────────────────────────────────────────────┘   │
│               │ generates                                       │
│               ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Applications: ollama, litellm, plex, sonarr, ...       │   │
│  │  (Individual app Applications - one per enabled app)    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Namespaces: <app-name>                                         │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  ollama          │  │  plex            │  │  sonarr      │  │
│  │  ├─Deployment    │  │  ├─StatefulSet   │  │  ├─Deploy   │  │
│  │  ├─Service       │  │  ├─Service       │  │  ├─Service  │  │
│  │  ├─Route         │  │  ├─Route         │  │  ├─Route    │  │
│  │  └─PVC           │  │  └─PVC           │  │  └─PVC      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎛️ Sync Waves

Sync waves control deployment order:

| Wave | Category         | Examples                                    |
| ---- | ---------------- | ------------------------------------------- |
| -5   | Pre-requisites   | Namespaces, ServiceAccounts                 |
| 0    | Security/Secrets | External Secrets Operator, cert-manager     |
| 50   | Storage          | TrueNAS CSI, Synology CSI                   |
| 100  | Applications     | Plex, Ollama, Home Assistant (most apps)    |
| 150  | GPU/Specialized  | GPU operators, device plugins               |
| 200  | Tweaks           | Network interface cleanup, snapshot cleanup |

**Defined in:** ApplicationSet templates via `argocd.argoproj.io/sync-wave` annotation

---

## 🔐 Security Model

```
┌─────────────────────────────────────────────────────────────┐
│  Platform-Level (Cluster-Scoped)                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  • StorageClass (TrueNAS, Synology)                   │ │
│  │  • ClusterRole/ClusterRoleBinding (operators only)    │ │
│  │  • SecurityContextConstraints (GPU operators only)    │ │
│  │  • CustomResourceDefinitions (operators)              │ │
│  └───────────────────────────────────────────────────────┘ │
│  Location: charts/platform/                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Application-Level (Namespace-Scoped)                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  • Namespace                                          │ │
│  │  • ServiceAccount (per app)                           │ │
│  │  • Role/RoleBinding (if needed)                       │ │
│  │  • Deployment/StatefulSet                             │ │
│  │  • Service, Route, PVC                                │ │
│  │  • ExternalSecret (app secrets)                       │ │
│  └───────────────────────────────────────────────────────┘ │
│  Location: charts/applications/<domain>/<app>/            │
│  Security Context: Restricted SCC compliant               │
│  • runAsNonRoot: true                                     │
│  • allowPrivilegeEscalation: false                        │
│  • capabilities.drop: [ALL]                               │
└─────────────────────────────────────────────────────────────┘
```

**Guardrail:** Applications **MUST NOT** include cluster-scoped resources.

**See:** [CHART-STANDARDS.md](../CHART-STANDARDS.md) for complete security requirements.

---

## 🌐 Multi-Cluster Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Hub Cluster (ACM/MCE)                                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  • Advanced Cluster Management                         │  │
│  │  • Policy Engine                                       │  │
│  │  │  Observability                                       │  │
│  │  • Cluster Lifecycle Management                        │  │
│  └────┬───────────────────────────────────────────────────┘  │
└───────┼──────────────────────────────────────────────────────┘
        │ manages
        ▼
┌───────────────────┬───────────────────┬──────────────────────┐
│                   │                   │                      │
│  Managed Cluster  │  Managed Cluster  │  Managed Cluster     │
│  (prod)           │  (test)           │  (hub itself)        │
│  ┌──────────────┐ │  ┌──────────────┐ │  ┌─────────────────┐ │
│  │ GitOps Pull  │ │  │ GitOps Pull  │ │  │ GitOps Pull     │ │
│  │ (autonomous) │ │  │ (autonomous) │ │  │ (autonomous)    │ │
│  └──────────────┘ │  └──────────────┘ │  └─────────────────┘ │
│  • Media stack    │  • Testing apps   │  • ACM/MCE          │
│  • AI stack       │  • Paperless      │  • Platform only    │
└───────────────────┴───────────────────┴──────────────────────┘
                    │
                    ▼
           ┌────────────────────┐
           │  Git Repository    │
           │  (Single source)   │
           │  • Cluster values  │
           │  • App charts      │
           └────────────────────┘
```

**Model:** Hub-and-spoke with **pull-based GitOps** (each cluster autonomous)

**See:**

- [ADR 008: Multi-Cluster Strategy](../decisions/008-multi-cluster-management-strategy.md)
- [ACM Getting Started](../ACM-GETTING-STARTED.md)
- [Deployment Options](../deployment/DEPLOYMENT-OPTIONS.md)

---

## 📚 Related Documentation

- **[Detailed Overview](../DETAILED-OVERVIEW.md)** - Complete architecture documentation
- **[ADR Index](../decisions/INDEX.md)** - Architectural decisions and rationale
- **[Values Hierarchy](../VALUES-HIERARCHY.md)** - Configuration inheritance details
- **[Chart Standards](../CHART-STANDARDS.md)** - Application chart requirements
- **[Configuration Guide](../CONFIGURATION-GUIDE.md)** - What to modify vs what not to
- **[Deployment Options](../deployment/DEPLOYMENT-OPTIONS.md)** - Choosing deployment patterns

---

**Last Updated:** 2025-11-07
**Purpose:** Quick visual reference to eliminate architecture repetition across docs
