---
applyTo: "**"
---

# Adding a New Application to the GitOps Repository

When the user asks to "add a chart", "create a chart", "add a new app/application", or "add <app-name>", automatically follow these steps.

## Overview

This repository uses an **ApplicationSet-based architecture**:

- Each `roles/<cluster>/` folder defines ALL ApplicationSets for a specific cluster
- ApplicationSets group apps by function (ai, media, security, etc.)
- Each ApplicationSet dynamically creates child Applications from a list
- Individual app charts live in `charts/applications/<domain>/<app>/`

## CRITICAL: Application Source Selection (ADR-004)

**Before creating any chart, you MUST follow the operator-first pattern defined in ADR-004:**

1. **Check for Kubernetes Operator FIRST** → Search [OperatorHub.io](https://operatorhub.io/) and [ArtifactHub.io](https://artifacthub.io/)
2. **If no operator: Search for Official Helm Chart** → [ArtifactHub.io](https://artifacthub.io/)
3. **If no chart: Use Official Container Images** → [Quay.io](https://quay.io/) or [Docker Hub](https://hub.docker.com/)

**Priority Tiers:**

- **Deployment Type:** Operators > Helm Charts > Custom Deployments
- **Source Quality:** Official/Red Hat Certified > Verified/Partners > CNCF > Community

**📚 Reference Documentation:**

- **ADR-004:** `docs/decisions/004-application-source-selection-priority.md`
- **Detailed Guide:** `docs/reference/PREFERRED-SOURCES.md`
- **Quick Reference (Print/Bookmark):** `docs/reference/APPLICATION-SOURCES-QUICK-REF.md`
- **Checklist:** `docs/instructions/adding-an-application-checklist.md`

## Steps to Add a New Application

### 1. Determine Target ApplicationSet

Choose which functional group the app belongs to:

- `ai` - AI/ML applications (LiteLLM, Ollama, JupyterHub, etc.)
- `media` - Media management (Plex, Sonarr, Radarr, Prowlarr, etc.)
- `base` - Infrastructure (Gatus, Goldilocks, VPA, Certificates, NFD, etc.)
- `home-automation` - IoT/Smart Home (Home Assistant, Node-RED, EMQX, etc.)
- `productivity` - Productivity tools (Bookmarks, CyberChef, Excalidraw, etc.)
- `security` - Security tools (External Secrets Operator, etc.)
- `storage` - Storage providers (TrueNAS CSI, Synology, etc.)
- `tweaks` - Cluster tweaks (Interface disablers, snapshot cleanup, etc.)

Each group has corresponding ApplicationSet templates in `roles/<cluster>/templates/`:

- `ai.yaml`, `media.yaml`, `home-automation.yaml`, `productivity.yaml`
- `base-apps.yaml`, `base-security.yaml`, `base-storage.yaml`, `base-tweaks.yaml`

### 2. Create the App Helm Chart

**Option A: Use the scaffold script**

```bash
./scripts/scaffold-new-chart.sh
```

**Option B: Manual creation**

Create directory structure under `charts/applications/<domain>/<app>/`:

```
charts/applications/<domain>/<app>/
├── Chart.yaml
├── values.yaml
├── crds/                      # (OPTIONAL) CustomResourceDefinitions
│   └── *.crd.yaml             # Pure YAML, no Helm templating
└── templates/
    ├── deployment.yaml (or statefulset.yaml)
    ├── service.yaml
    ├── route.yaml (if web app)
    ├── pvc.yaml (if needs storage)
    ├── securitycontextconstraints.yaml (if needs special permissions)
    ├── links.yaml (optional - ConsoleLink for OpenShift)
    └── gatus-config.yaml (optional - health monitoring)
```

**IMPORTANT: CRD Placement**

- CRDs **MUST** be placed in `crds/` directory, not `templates/`
- Helm installs CRDs **before** any other resources automatically
- CRDs in `crds/` do NOT support Helm templating (`{{ }}` syntax)
- CRDs in `crds/` do NOT respect sync-wave annotations
- See "CRD Management" section below for details

**Chart.yaml example:**

```yaml
apiVersion: v2
name: <app-name>
description: A Helm chart for <App Name>
version: 1.0.0
kubeVersion: ">=1.22.0-0"

maintainers:
  - name: Roy Bales
    email: rbales79@gmail.com
```

**values.yaml structure:**

```yaml
cluster:
  top_level_domain: roybales.com
  name: cluster
  admin_email: rbales79@gmail.com
  timezone: America/New_York

application:
  name: App Name
  group: Domain
  icon: mdi:icon-name
  iconColor: ""
  image: "https://example.com/logo.png"
  description: "App description"
  port: 8080
  location: 100

pods:
  main:
    image:
      repository: docker.io/org/app
      # renovate: datasource=docker depName=docker.io/org/app versioning=semver
      tag: "1.0.0"

gatus:
  enabled: true
  interval: 5m
  conditions:
    - "[STATUS] == 200"
    - "[RESPONSE_TIME] < 3000"
```

### 3. Add App to ApplicationSet(s)

**IMPORTANT:** Add the app to the ApplicationSet in **ALL** cluster roles unless it's cluster-specific.

Edit `roles/sno/templates/<group>.yaml`, `roles/hub/templates/<group>.yaml`, and `roles/test/templates/<group>.yaml`:

In the `generators.list.elements` array, add:

```yaml
- name: <app-name>
  group: <domain> # e.g., ai, media, productivity
  gatus:
    enabled: true # optional, for health monitoring
```

**Example for adding to AI group:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {{ .Release.Name }}-ai
  annotations:
    argocd.argoproj.io/sync-wave: "100"
spec:
  generators:
    - list:
        elements:
          - name: litellm
            group: ai
            gatus:
              enabled: true
          - name: open-webui
            group: ai
            gatus:
              enabled: true
          - name: jupyter-hub  # ← NEW APP
            group: ai
            gatus:
              enabled: true
```

### 4. Configure App Templates

Create Kubernetes manifests in `charts/applications/<domain>/<app>/templates/`:

**Key patterns to follow:**

- Use `{{ .Release.Name }}` for resource names
- Routes: `{{ .Release.Name }}.apps.{{ .Values.cluster.name }}.{{ .Values.cluster.top_level_domain }}`
- Reference values: `{{ .Values.cluster.timezone }}`, `{{ .Values.pods.main.image.repository }}`
- Add renovate comments above image tags for automated updates
- Include gatus monitoring config if app has HTTP endpoint

### 5. Test Locally

Validate the ApplicationSet generates correctly:

```bash
# Render the ApplicationSet
helm template sno ./roles/sno -s templates/<group>.yaml

# Render the full app chart
helm template <app-name> ./charts/applications/<domain>/<app>/

# Lint the app chart
helm lint charts/applications/<domain>/<app>/
```

### 6. Commit and Monitor

After committing changes:

```bash
# Check ApplicationSets
oc get applicationset -n openshift-gitops

# Check if new Application was created
oc get application <app-name> -n openshift-gitops

# Monitor app deployment
oc get pods -n <app-name>
oc logs -n <app-name> -l app=<app-name>
```

## Adding a New ApplicationSet Category

If you need to create an entirely new functional group (rare):

1. **Create template in all cluster roles:** `roles/sno/templates/<new-category>.yaml`, etc.

2. **Follow existing pattern:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {{ .Release.Name }}-<category>
  annotations:
    argocd.argoproj.io/sync-wave: "100"  # 0=security, 50=storage, 100=apps, 200=tweaks
spec:
  ignoreApplicationDifferences:
    - jsonPointers:
        - /spec/syncPolicy
  goTemplate: true
  generators:
    - list:
        elements:
          - name: app1
            group: <category>
  template:
    metadata:
      name: '{{ "{{" }} .name {{ "}}" }}'
      namespace: "openshift-gitops"
    spec:
      project: default
      destination:
        server: {{ .Values.spec.destination.server }}
        namespace: '{{ "{{" }} .name {{ "}}" }}'
      syncPolicy:
        managedNamespaceMetadata:
          labels:
            goldilocks.fairwinds.com/enabled: "true"
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
      source:
        repoURL: {{ .Values.spec.source.repoURL }}
        path: charts/{{ "{{" }} default "<category>" .group {{ "}}" }}/{{ "{{" }} .name {{ "}}" }}
        targetRevision: {{ .Values.spec.source.targetRevision }}
        helm:
          valuesObject:
            # Pass cluster config to apps
            spec:
{{ .Values.spec | toYaml | nindent 14 }}
{{ .Values.config | toYaml | nindent 12 }}
```

3. **Replicate across all cluster roles** (sno, hub, test, template)

## CRD Management

### When to Use the `crds/` Directory

Place CustomResourceDefinitions in `charts/applications/<domain>/<app>/crds/` when:

- The app is an operator (e.g., MetalLB, EMQX Operator, cert-manager)
- The app creates custom resources (e.g., `IPAddressPool`, `Certificate`, `ExternalSecret`)
- The app requires CRDs to be installed before any other resources

### CRD Directory Rules

**CRITICAL:** CRDs in the `crds/` directory have special behavior:

1. **Installation Timing:** Helm installs CRDs **before any other chart resources**, regardless of sync-wave annotations
2. **No Templating:** CRDs in `crds/` do NOT support Helm templating (`{{ }}` syntax will break)
3. **No Sync Waves:** `argocd.argoproj.io/sync-wave` annotations are ignored for CRDs in `crds/`
4. **Upgrade Limitations:** Helm does NOT automatically upgrade CRDs (manual deletion/recreation may be needed)

### CRD File Structure

```
charts/applications/<domain>/<app>/
├── Chart.yaml
├── values.yaml
├── crds/                          # ← CRDs go here
│   └── <resource>.crd.yaml        # Pure YAML, no Helm templates
└── templates/
    ├── deployment.yaml
    ├── custom-resource.yaml       # Uses the CRD defined above
    └── ...
```

### Example: MetalLB CRDs

```yaml
# charts/infrastructure/metallb/crds/metallb-crds.yaml
---
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: ipaddresspools.metallb.io
spec:
  group: metallb.io
  names:
    kind: IPAddressPool
    plural: ipaddresspools
  # ... (no Helm templating allowed here)
```

Then in templates, create instances:

```yaml
# charts/infrastructure/metallb/templates/ipaddresspool.yaml
---
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: {{ .Values.poolName }}
  namespace: {{ .Release.Namespace }}
spec:
  addresses:
  {{- range .Values.addresses }}
  - {{ . }}
  {{- end }}
```

### Common CRD Sync Errors

- **"The Kubernetes API could not find <kind>"** → CRD not installed; check if it's in `crds/` or `templates/`
- **"no matches for kind"** → CRD missing or not installed yet; move to `crds/` directory
- **"Helm template error in crds/"** → Remove all `{{ }}` Helm syntax from CRD files
- **"one or more synchronization tasks are not valid"** → Usually means CRDs are missing or in wrong location

### When NOT to Use `crds/` Directory

- For simple apps without custom resources (Deployments, Services, Routes are standard Kubernetes resources)
- When you need to conditionally install CRDs based on Helm values (use templates/ instead, but ensure sync-wave=-5)
- For resources that use CRDs but aren't CRDs themselves (e.g., an `IPAddressPool` instance uses the CRD but isn't one)

## Key Conventions

- **App names:** Lowercase, match the actual application (e.g., `home-assistant`, `open-webui`)
- **ApplicationSet names:** `{{ .Release.Name }}-<category>` becomes `sno-ai`, `hub-media`, etc.
- **Namespaces:** Auto-created per app, matches app name
- **Routes:** `<app>.apps.<cluster>.<domain>` (e.g., `litellm.apps.sno.roybales.com`)
- **Sync waves:** 0 (security), 50 (storage), 100 (apps), 200 (tweaks)
- **CRDs:** Always in `crds/` directory, installed before sync waves

## Common Mistakes to Avoid

- ❌ Only adding app to one cluster role → Add to ALL (sno, hub, test) unless cluster-specific
- ❌ Hardcoding domains → Use `{{ .Values.cluster.top_level_domain }}`
- ❌ Missing renovate comments → Image updates won't be automated
- ❌ Wrong sync wave → Apps deploy before dependencies
- ❌ Forgetting `managedNamespaceMetadata` → VPA/Goldilocks won't work
- ❌ CRDs in templates/ instead of crds/ → If an app requires CRDs, place them in `crds/` directory, not `templates/`. CRDs in templates/ may cause sync failures due to ordering issues.
- ❌ Helm templating in CRDs → CRD files in `crds/` directory must be pure YAML without any `{{ }}` Helm syntax.
