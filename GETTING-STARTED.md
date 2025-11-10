# Getting Started with OpenShift GitOps

This guide will get you up and running with this GitOps repository in under 30 minutes.

## What Is This?

This repository uses the **Red Hat Validated Patterns Framework** to deploy and manage applications on OpenShift clusters using GitOps principles. One bootstrap Application manages everything.

### Architecture (3 Levels)

```
Bootstrap Application (manual)
    ↓
Role Chart (Helm) - Deploys ApplicationSet deployers
    ↓
ApplicationSets (Helm) - Generate child Applications
    ↓
Application Charts (Helm) - Individual apps (Plex, Ollama, etc.)
```

### Configuration Hierarchy

```
values-global.yaml       # Pattern defaults (all clusters)
  ↓
clusters/sets/values-home.yaml         # Cluster set (home lab, work lab, cloud)
└──
clusters/individual-clusters/values-prod.yaml         # Specific cluster (prod, hub, test)
```

## Prerequisites

- OpenShift/OKD 4.12+ cluster
- `oc` CLI authenticated with cluster-admin
- Git repository forked from this repo
- **Infisical account** for secrets management ([app.infisical.com](https://app.infisical.com) - free tier available)

## Quick Start (35 minutes)

### 1. Install Argo CD (2 minutes)

```bash
# Check if OpenShift GitOps is already installed
# NOTE: The operator is installed cluster-wide (check CSV in all namespaces)
oc get csv -n openshift-gitops | grep openshift-gitops-operator

# If not installed, install OpenShift GitOps operator
oc apply -f - <<EOF
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-gitops-operator
  namespace: openshift-operators
spec:
  channel: latest
  name: openshift-gitops-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF

# Wait for operator to be ready
oc wait --for=condition=ready pod -l app.kubernetes.io/name=openshift-gitops-server \
  -n openshift-gitops --timeout=300s
```

### 2. Grant Argo CD Permissions (1 minute)

```bash
# Give Argo CD cluster-admin (required for CRDs, operators, etc.)
oc apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: openshift-gitops-cluster-admin
subjects:
  - kind: ServiceAccount
    name: openshift-gitops-argocd-application-controller
    namespace: openshift-gitops
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
EOF
```

### 3. Configure Infisical Secrets (5 minutes)

**Why Infisical?** Stores sensitive data (API keys, passwords) outside Git using External Secrets Operator.

#### Option A: Use Infisical (Recommended)

**Step 1: Create Infisical Project**

1. Sign up at [Infisical Cloud](https://app.infisical.com) (free tier available)
2. Create a new project (e.g., "homelab" or "openshift-prod")
3. Create an environment (e.g., "prod")
4. Add secrets to your project:
   - Certificates: `CLOUDFLARE_API_TOKEN` (for Let's Encrypt DNS validation)
   - Storage: `TRUENAS_API_KEY`, `TRUENAS_HOST`
   - Applications: API keys for apps (Plex claim token, etc.)

**Step 2: Create Service Token**

1. In Infisical project settings → Service Tokens → Create Token
2. Give it a name (e.g., "openshift-cluster")
3. Select environment (prod)
4. Copy the service token (starts with `st.`)

**Step 3: Create Kubernetes Secret**

```bash
# Create Infisical authentication secret
oc create secret generic infisical-auth-secret \
  -n openshift-gitops \
  --from-literal=serviceToken='YOUR_SERVICE_TOKEN_HERE'
```

**Step 4: Update your values file**

Edit `values-mycluster.yaml`:

```yaml
clusterGroup:
  platformComponents:
    externalSecrets:
      enabled: true

  externalSecrets:
    backend: infisical
    secret: infisical-auth-secret
    infisical:
      projectSlug: homelab # Your Infisical project slug
      environmentSlug: prod # Your environment (prod, dev, staging)
      apiUrl: https://app.infisical.com
```

#### Option B: Skip Secrets (Testing Only)

For testing without secrets, disable External Secrets Operator:

```yaml
clusterGroup:
  platformComponents:
    externalSecrets:
      enabled: false
    certManager:
      enabled: false # Requires secrets for DNS validation
```

**⚠️ Warning:** Many apps require secrets (certificates, API keys). Without ESO, you'll need to create secrets manually.

### 4. Configure Your Cluster (3 minutes)

**Option A: Use existing cluster values** (recommended for testing)

```bash
# Copy and edit one of the example values files
cp clusters/individual-clusters/values-test.yaml clusters/individual-clusters/values-mycluster.yaml
```

Edit `values-mycluster.yaml`:

- Change `clusterGroup.name` to your cluster name
- Update `cluster.domain` and `cluster.apps_domain`
- Enable/disable apps in `applicationStacks` sections
- Comment out any platform components you don't need

**Option B: Start from scratch**

See [docs/operations/CLUSTER-BOOTSTRAP.md](docs/operations/CLUSTER-BOOTSTRAP.md) for complete examples.

### 5. Create Bootstrap Application (2 minutes)

```bash
# Create the "cluster" Application pointing to your role
oc apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cluster
  namespace: openshift-gitops
spec:
  project: default
  source:
    repoURL: https://github.com/YOUR_USERNAME/argo-apps
    targetRevision: HEAD
    path: roles/sno  # or roles/hub, roles/test
    helm:
      valueFiles:
        - ../../values-global.yaml
        - ../../values-mycluster.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: openshift-gitops
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
EOF
```

### 6. Watch the Magic (5 minutes)

```bash
# Watch ApplicationSet deployers get created
oc get applications -n openshift-gitops -w

# Watch ApplicationSets get created
oc get applicationsets -n openshift-gitops -w

# Watch individual apps deploy
oc get applications -A | grep -v openshift-gitops

# Check specific app
oc get pods -n plex
```

### 7. Access Argo CD UI (2 minutes)

```bash
# Get the route
oc get route openshift-gitops-server -n openshift-gitops

# Get the admin password
oc extract secret/openshift-gitops-cluster \
  -n openshift-gitops --to=-
```

Navigate to the route URL, login as `admin` with the password.

## Understanding the Architecture

### What Just Happened?

1. **Bootstrap Application** deployed your role chart from `roles/<cluster>/`
2. **Role chart** created ApplicationSet deployer Applications:
   - `platform-applicationset` → `charts/platform/`
   - `ai-applicationset` → `charts/applications/ai/`
   - `media-applicationset` → `charts/applications/media/`
   - etc.
3. **ApplicationSet deployers** created the master ApplicationSets
4. **Master ApplicationSets** generated child Applications for each enabled app
5. **Child Applications** deployed the actual Helm charts

### Directory Structure

```
roles/
  sno/                        # Your cluster role
    templates/
      platform-applicationset.yaml   # Deploys charts/platform/
      media-applicationset.yaml      # Deploys charts/applications/media/

charts/
  platform/                   # Platform components
    templates/
      applicationset.yaml     # Master ApplicationSet (generates apps)
    external-secrets-operator/
    certificates/
    truenas/
    gatus/
    ...

  applications/               # User applications
    media/
      templates/
        applicationset.yaml   # Master ApplicationSet (generates apps)
      plex/
      sonarr/
      radarr/
      ...
    ai/
      ollama/
      open-webui/
      ...
```

### Configuration Flow

```yaml
# values-global.yaml
clusterGroup:
  platformComponents:
    certManager:
      enabled: true  # Default for all clusters

# values-mycluster.yaml
clusterGroup:
  platformComponents:
    certManager:
      enabled: false  # Override: disable for this cluster

  applicationStacks:
    media:
      enabled: true
      apps:
        - plex        # Enable Plex
        - sonarr      # Enable Sonarr
        # - radarr    # Disabled (commented)
```

## Common Tasks

### Enable an Application

Edit `values-mycluster.yaml`:

```yaml
applicationStacks:
  ai:
    enabled: true
    apps:
      - ollama # Uncomment to enable
      - open-webui # Uncomment to enable
```

Commit and push - Argo CD syncs automatically.

### Disable an Application

Comment out or remove from the list:

```yaml
applicationStacks:
  ai:
    enabled: true
    apps:
      # - ollama      # Commented = disabled
      - open-webui # Still enabled
```

### Add a New Application

1. Create chart: `charts/applications/<domain>/<app>/`
2. Add to values files: `scripts/generate-app-list-template.py`
3. Verify: `scripts/verify-app-inventory.sh`
4. See [.github/instructions/adding-an-application-checklist.md](../.github/instructions/adding-an-application-checklist.md)

### Change Configuration

Edit the values file and commit:

```yaml
applications:
  plex:
    storage:
      media:
        size: 2Ti # Change from default
```

Argo CD detects the change and syncs.

### Troubleshoot Failed Sync

```bash
# Check Application status
oc describe application plex -n openshift-gitops

# Check pod logs
oc logs -n plex -l app=plex

# Manual sync
oc patch application plex -n openshift-gitops \
  --type merge -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{}}}'
```

## Next Steps

- **[Cluster Bootstrap Guide](docs/operations/CLUSTER-BOOTSTRAP.md)** - Detailed step-by-step setup
- **[Chart Standards](docs/CHART-STANDARDS.md)** - Creating compliant charts
- **[Change Management](docs/CHANGE-MANAGEMENT.md)** - Making safe changes
- **[Values Hierarchy](docs/VALUES-HIERARCHY.md)** - Understanding configuration
- **[Troubleshooting](docs/troubleshooting/)** - Common issues and fixes

## Quick Reference

### Repository Structure

- `values-*.yaml` - Cluster configuration files
- `roles/` - Cluster role definitions (SNO, Hub, Test)
- `charts/platform/` - Infrastructure components (22 charts)
- `charts/applications/` - User applications (38+ apps across 5 domains)
- `docs/operations/` - Operational guides (bootstrap, kubeconfig, ACM)
- `docs/` - Complete documentation
- `scripts/` - Utility scripts for maintenance

### Key Commands

```bash
# Check what Argo CD sees
oc get applications -A

# Force sync
oc patch application <name> -n openshift-gitops --type merge \
  -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{}}}'

# Render what will deploy
helm template mycluster ./roles/sno \
  -f values-global.yaml \
  -f values-mycluster.yaml

# Verify chart standards
python3 scripts/audit/audit-chart-standards.py --chart charts/applications/media/plex
```

### Available Roles

- **sno** - Single Node OpenShift (1 node, minimal resources)
- **compact** - 3-node cluster (2-3 replicas, PDBs)
- **full** - 6+ node HA cluster (3+ replicas, full PDBs)
- **hub** - Management cluster (ACM/MCE enabled)
- **test** - Testing cluster (minimal apps)

### Application Domains

- **ai** - AI/ML (ollama, open-webui, litellm)
- **media** - Media management (plex, sonarr, radarr, overseerr, etc.)
- **home-automation** - IoT (home-assistant, node-red, emqx)
- **productivity** - Tools (bookmarks, cyberchef, excalidraw)
- **infrastructure** - Special apps (paperless, adsb, glue-worker)

### Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Credit**: Based on [ullbergm/openshift](https://github.com/ullbergm/openshift)
