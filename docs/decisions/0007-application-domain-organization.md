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

# ADR 007: Application Domain Organization

## Context and Problem Statement

As the number of applications grew from a handful to 38+, we needed a clear organizational structure:

1. **Functional Grouping:** Related applications should be grouped together
2. **ApplicationSet Manageability:** ApplicationSets with too many apps become unwieldy
3. **Enable/Disable Granularity:** Ability to enable entire domains or individual apps
4. **Clear Ownership:** Domain boundaries help distribute responsibility
5. **Documentation Structure:** Domain-specific instructions and troubleshooting
6. **Deployment Dependencies:** Some apps within a domain depend on each other

Without clear domain organization, the ApplicationSet structure becomes a flat list that's difficult to manage and understand.

## Decision Drivers

- ApplicationSets work best with 5-15 applications each
- Functional domains align with team expertise (AI/ML, media, IoT, etc.)
- Domain-level enable/disable simplifies cluster configuration
- Clear naming patterns aid discovery
- Separation of concerns between application types
- Support for domain-specific configurations (storage paths, resource requirements)

## Considered Options

1. **Single ApplicationSet** - All apps in one flat list
2. **Cluster-Based Domains** - Separate by deployment location (prod, test, hub)
3. **Technology-Based Domains** - Group by tech stack (Python, Node.js, Go)
4. **Functional Domains** - Group by business function (chosen)
5. **Layer-Based Domains** - Separate by stack layer (frontend, backend, data)

## Decision Outcome

Chosen option: **Functional Domains**, because they align with how users think about applications and support clear ownership boundaries.

### Domain Structure

Five primary application domains:

#### 1. **AI** (`charts/applications/ai/`)

**Purpose:** Artificial Intelligence and Machine Learning applications

**Applications (3):**

- `litellm` - LLM proxy/router with unified API
- `ollama` - Local LLM inference engine
- `open-webui` - Web interface for LLM interaction

**Characteristics:**

- GPU-dependent (require GPU operator)
- High compute requirements
- Shared model storage (NFS/PVC)
- Long-running inference workloads

**Domain-Level Configuration:**

```yaml
clusterGroup:
  applicationStacks:
    ai:
      enabled: true
      modelStorage:
        size: 100Gi
        storageClass: truenas-nfs
      gpuRequired: true
      apps:
        - litellm
        - ollama
        - open-webui
```

#### 2. **Media** (`charts/applications/media/`)

**Purpose:** Media management and streaming applications

**Applications (14):**

- `plex` - Media server
- `sonarr` - TV show management
- `radarr` - Movie management
- `lidarr` - Music management
- `readarr` - Book/audiobook management
- `prowlarr` - Indexer management
- `overseerr` - Request management
- `tautulli` - Plex analytics
- `unpackerr` - Archive extraction
- `sabnzbd` - Usenet downloader
- `qbittorrent` - BitTorrent client
- `flaresolverr` - Cloudflare bypass
- `recyclarr` - Configuration sync
- `tdarr` - Transcoding automation

**Characteristics:**

- Large storage requirements (media libraries)
- Interdependent (Prowlarr → Sonarr/Radarr → Download clients)
- Shared data mounts across apps
- Ingress/routing critical (web UIs)

**Domain-Level Configuration:**

```yaml
clusterGroup:
  applicationStacks:
    media:
      enabled: true
      sharedPaths:
        media: /mnt/media
        downloads: /mnt/downloads
        config: /mnt/config
      storageClass: truenas-nfs
      apps:
        - plex
        - sonarr
        - radarr
```

#### 3. **Home Automation** (`charts/applications/home-automation/`)

**Purpose:** IoT, smart home, and automation applications

**Applications (5):**

- `home-assistant` - Home automation platform
- `node-red` - Visual workflow automation
- `emqx-operator` - MQTT broker operator
- `zwavejs2mqtt` - Z-Wave to MQTT gateway
- `zigbee2mqtt` - Zigbee to MQTT gateway

**Characteristics:**

- Real-time communication (MQTT, WebSockets)
- Hardware dependencies (USB devices for Z-Wave/Zigbee)
- Low latency requirements
- Persistent state critical

**Domain-Level Configuration:**

```yaml
clusterGroup:
  applicationStacks:
    home-automation:
      enabled: true
      mqtt:
        enabled: true
        broker: emqx
      hardware:
        usb_devices: true
      apps:
        - emqx-operator
        - home-assistant
        - node-red
```

#### 4. **Productivity** (`charts/applications/productivity/`)

**Purpose:** Personal productivity and utility tools

**Applications (9):**

- `bookmarks` - Bookmark manager (Linkwarden)
- `cyberchef` - Data transformation toolkit
- `excalidraw` - Diagram/whiteboard tool
- `it-tools` - Developer utilities
- `startpunkt` - Personal dashboard/startpage
- `homepage` - Application dashboard
- `linkding` - Bookmark manager (alternative)
- `stirling-pdf` - PDF manipulation tools
- `actual-budget` - Personal finance

**Characteristics:**

- Lightweight workloads
- User-facing web interfaces
- Minimal dependencies
- Personal data storage (bookmarks, notes)

**Domain-Level Configuration:**

```yaml
clusterGroup:
  applicationStacks:
    productivity:
      enabled: true
      sso:
        enabled: false # Most are personal tools
      apps:
        - bookmarks
        - cyberchef
        - excalidraw
```

#### 5. **Infrastructure** (`charts/applications/infrastructure/`)

**Purpose:** Supporting infrastructure and operations applications

**Applications (7):**

- `paperless-ngx` - Document management
- `paperless-gpt` - AI document processing
- `paperless-postprocessing` - Document workflow
- `adsb` - ADS-B flight tracking
- `glue-worker` - Custom integration worker
- `emqx-operator` - MQTT broker operator (also in home-automation)
- `monitoring-stack` - Prometheus/Grafana (future)

**Characteristics:**

- Operational support services
- Integration/middleware applications
- May have external dependencies
- Less user-facing

**Domain-Level Configuration:**

```yaml
clusterGroup:
  applicationStacks:
    infrastructure:
      enabled: true
      operators:
        enabled: true
      apps:
        - paperless-ngx
        - glue-worker
```

### Master ApplicationSet Pattern

Each domain has a master ApplicationSet chart at `charts/applications/<domain>/`:

```
charts/applications/<domain>/
├── Chart.yaml
├── values.yaml
├── templates/
│   └── applicationset.yaml    # Master ApplicationSet template
└── <app1>/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
```

**Master ApplicationSet Template Structure:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: {{ .Release.Name }}-<domain>
  namespace: openshift-gitops
  annotations:
    argocd.argoproj.io/sync-wave: "100"  # Apps after platform
spec:
  generators:
    - list:
        elements:
          {{- range .Values.clusterGroup.applicationStacks.<domain>.apps }}
          - name: {{ . }}
            group: <domain>
          {{- end }}
  template:
    metadata:
      name: "{{ "{{name}}" }}"
      labels:
        application-group: <domain>
    spec:
      project: default
      source:
        repoURL: {{ .Values.clusterGroup.gitRepoUrl }}
        targetRevision: {{ .Values.clusterGroup.targetRevision }}
        path: charts/applications/<domain>/{{ "{{name}}" }}
        helm:
          valuesObject:
            cluster: {{ .Values.cluster | toYaml | nindent 14 }}
            application: {{ .Values.application | toYaml | nindent 14 }}
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{ "{{name}}" }}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
        managedNamespaceMetadata:
          labels:
            goldilocks.fairwinds.com/enabled: "true"
```

### Role Chart Integration

Each role deploys ApplicationSet deployer Applications:

```yaml
# roles/<topology>/templates/ai-applicationset.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ai-applicationset
  namespace: openshift-gitops
spec:
  source:
    repoURL: { { .Values.clusterGroup.gitRepoUrl } }
    targetRevision: { { .Values.clusterGroup.targetRevision } }
    path: charts/applications/ai
    helm:
      values: |
        {{ .Values | toYaml | nindent 8 }}
  destination:
    server: https://kubernetes.default.svc
    namespace: openshift-gitops
```

### Consequences

**Good:**

- ✅ Clear functional boundaries (AI, Media, Home Automation, etc.)
- ✅ Manageable ApplicationSet sizes (3-14 apps per domain)
- ✅ Domain-level enable/disable simplifies configuration
- ✅ Domain-specific settings (storage paths, GPU requirements)
- ✅ Supports domain-specific documentation
- ✅ Clear ownership and expertise alignment
- ✅ Easy to add new domains without restructuring

**Bad:**

- ❌ Some apps could fit multiple domains (EMQX in both home-automation and infrastructure)
- ❌ Domain boundaries not always clear-cut
- ❌ Adding a domain requires new ApplicationSet chart
- ❌ Cross-domain dependencies require coordination

**Neutral:**

- 🔄 Five domains currently, may grow over time
- 🔄 Applications can move between domains (requires chart relocation)
- 🔄 Domain-specific instructions in `docs/instructions/domains/<domain>.md`

### Confirmation

Domain organization is working correctly if:

1. **ApplicationSets Deployed:**

   ```bash
   oc get applicationset.argoproj.io -n openshift-gitops
   # Should show: <cluster>-ai, <cluster>-media, <cluster>-home-automation, etc.
   ```

2. **Domain-Level Control:**

   ```bash
   # Disabling a domain disables all its apps
   # In values-<cluster>.yaml:
   # applicationStacks:
   #   media:
   #     enabled: false  # All media apps disabled
   ```

3. **Applications Grouped:**

   ```bash
   oc get applications.argoproj.io -n openshift-gitops -l application-group=media
   # Should show all media applications
   ```

4. **Documentation Structure:**
   ```bash
   ls docs/instructions/domains/
   # Should have: ai.md, media.md, home-automation.md, productivity.md, infrastructure.md
   ```

## Pros and Cons of the Options

### Single ApplicationSet (Flat List)

- Good: Simplest structure
- Good: Single place to manage all apps
- Bad: Unwieldy with 38+ apps
- Bad: No functional grouping
- Bad: Can't enable/disable groups
- Bad: Poor separation of concerns

### Cluster-Based Domains

- Good: Maps to deployment locations
- Bad: Duplicates apps across environments
- Bad: No functional organization
- Bad: Doesn't help with application relationships
- Bad: Production/test distinction, not functionality

### Technology-Based Domains

- Good: Groups similar tech stacks
- Bad: Users don't think in terms of programming languages
- Bad: Cross-stack applications difficult to categorize
- Bad: Doesn't reflect functional use cases
- Bad: Media apps span multiple technologies

### Functional Domains (Chosen)

- Good: Aligns with user mental models
- Good: Clear ownership boundaries
- Good: Supports domain-specific configuration
- Good: Enable/disable entire application stacks
- Bad: Some apps span multiple domains
- Bad: Requires decisions about categorization

### Layer-Based Domains

- Good: Technical separation (frontend/backend/data)
- Bad: Most apps are full-stack
- Bad: Breaks logical application groupings
- Bad: Doesn't match user workflows
- Bad: Media/AI apps have all layers

## Links

- **Domain Instructions:** `docs/instructions/domains/<domain>.md` - Domain-specific guides
- **ApplicationSet Charts:** `charts/applications/<domain>/` - Master ApplicationSet definitions
- **Adding Domains:** `docs/instructions/adding-a-new-domain.md` - How to create new domains
- **Related ADRs:**
  - ADR 002: Validated Patterns Framework (ApplicationSet architecture)
  - ADR 004: Application Source Selection (domain-agnostic)
- **Application Inventory:** Generated by `scripts/generate-app-list-template.py`

## Notes

- **Cross-Domain Apps:** Some operators (EMQX) appear in multiple domains - documented as intentional duplication
- **Domain Growth:** New domains can be added without affecting existing ones
- **ApplicationSet Sync Waves:** All application domains use sync-wave 100 (after platform at 0-50)
- **Namespace per App:** Each app gets its own namespace matching app name
- **Domain Documentation:** Each domain requires corresponding `docs/instructions/domains/<domain>.md`
