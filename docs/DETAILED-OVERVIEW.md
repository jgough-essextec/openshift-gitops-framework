# OpenShift GitOps with Validated Patterns

[![OpenShift](https://img.shields.io/badge/OpenShift-4.12+-red)](https://www.redhat.com/en/technologies/cloud-computing/openshift)
[![Validated Patterns](https://img.shields.io/badge/Framework-Validated%20Patterns-blue)](https://validatedpatterns.io/)
[![GitOps](https://img.shields.io/badge/GitOps-Argo%20CD-orange)](https://argoproj.github.io/cd/)

**One Git repo to rule them all.** Deploy and manage OpenShift clusters with GitOps using the Red Hat Validated Patterns Framework.

**⚡ Quick Start:** [GETTING-STARTED.md](GETTING-STARTED.md) - Get running in 30 minutes

**Credit:** Based on the excellent work by [Magnus Ullberg](https://github.com/ullbergm/openshift)

## What's Inside?

- **🎯 22 Platform Components** - External Secrets, Certificates, Storage (TrueNAS/Synology), MetalLB, GPU Operators, VPA, Gatus, ACM/MCE
- **📦 38+ Applications** - Media (Plex, Sonarr, Radarr), AI (Ollama, LiteLLM), Home Automation (Home Assistant, Node-RED), Productivity
- **🏗️ 3-Level Architecture** - Bootstrap → ApplicationSet Deployers → ApplicationSets → Applications
- **⚙️ Values-Driven Config** - Hierarchical configuration (global → cluster set → cluster)
- **🔄 Multi-Cluster Ready** - Manage home lab, work lab, and cloud clusters from one repo

## Architecture

```
Bootstrap Application (manual one-time setup)
    ↓
Role Chart (sno/hub/test) - Deploys ApplicationSet deployers
    ↓
ApplicationSets - Generate child Applications from enabled list
    ↓
Applications - Individual Helm charts (Plex, Ollama, etc.)
```

**Configuration:**
`values-global.yaml` (pattern defaults) → `clusters/sets/values-home.yaml` (cluster set) → `clusters/individual-clusters/values-prod.yaml` (specific cluster)

![Architecture Diagram](docs/images/chart-hierarchy.png)

## Repository Structure

```text
├── docs/                      # Documentation
│   ├── operations/            # Operational guides
│   │   ├── CLUSTER-BOOTSTRAP.md      # Step-by-step cluster setup guide
│   │   ├── KUBECONFIG-MANAGEMENT.md  # Multi-cluster credentials
│   │   └── acm/               # ACM operational guides
│   ├── decisions/             # Architectural Decision Records
│   ├── deployment/            # Deployment pattern guides
│   └── instructions/          # Step-by-step workflows
├── values-global.yaml         # Pattern-wide defaults (inherited by all clusters)
├── clusters/                  # Values file organization
│   ├── individual-clusters/  # Per-cluster values
│   │   ├── values-prod.yaml  # Production cluster configuration
│   │   ├── values-hub.yaml   # Hub cluster configuration
│   │   └── values-test.yaml  # Test cluster configuration
│   ├── sets/                 # Cluster set values
│   └── topologies/           # Topology defaults
├── roles/                     # Cluster role definitions (minimal Helm charts)
│   ├── sno/                   # Single Node OpenShift role
│   │   ├── Chart.yaml         # Chart metadata
│   │   └── templates/         # ApplicationSet deployer Applications
│   │       ├── platform-applicationset.yaml  # Deploys platform ApplicationSet
│   │       ├── ai-applicationset.yaml        # Deploys AI ApplicationSet
│   │       ├── media-applicationset.yaml     # Deploys media ApplicationSet
│   │       └── ...
│   ├── hub/                   # Hub/management cluster role
│   ├── test/                  # Testing cluster role
│   └── template/              # Reference template for new clusters
└── charts/                    # Helm charts (ApplicationSets and applications)
    ├── ai/
    │   ├── litellm/           # LiteLLM proxy for LLM management
    │   ├── ollama/            # Local LLM runtime
    │   └── open-webui/        # Web UI for LLMs
    ├── infrastructure/
  │   ├── gatus/             # Service monitoring and health checks
  │   ├── goldilocks/        # VPA recommendations dashboard
  │   ├── democratic-csi-synology-iscsi/ # Synology iSCSI storage driver
  │   └── democratic-csi-synology-nfs/   # Synology NFS storage driver
    ├── media/
    │   ├── bazarr/            # Subtitle management
    │   ├── flaresolverr/      # Cloudflare proxy solver
    │   ├── gaps/              # Media gap detection
    │   ├── huntarr/           # Wanted movie management
    │   ├── kapowarr/          # Comic book management
    │   ├── kavita/            # Digital library and comic reader
    │   ├── lidarr/            # Music collection management
    │   ├── metube/            # YouTube downloader web UI
    │   ├── overseerr/         # Media request management
    │   ├── pinchflat/         # YouTube channel archiver
    │   ├── plex/              # Media server
    │   ├── prowlarr/          # Indexer management
    │   ├── radarr/            # Movie collection management
    │   ├── readarr/           # Book and audiobook management
    │   ├── sabnzbd/           # Usenet downloader
    │   ├── sonarr/            # TV series management
    │   └── tautulli/          # Plex analytics and monitoring
    ├── productivity/
    │   ├── bookmarks/         # Bookmark management
    │   ├── cyberchef/         # Data manipulation toolkit
    │   ├── excalidraw/        # Whiteboard and diagramming
    │   ├── it-tools/          # Collection of IT utilities
    │   └── startpunkt/        # Homepage and dashboard
    └── security/
        └── external-secrets-operator/ # External secrets management
```

## Documentation

### 📖 Core Guides

- **[Getting Started](../GETTING-STARTED.md)** - Quick start guide (30 minutes to deployment)
- **[Cluster Bootstrap](operations/CLUSTER-BOOTSTRAP.md)** - Complete step-by-step setup with secrets
- **[Chart Standards](CHART-STANDARDS.md)** - How to create compliant Helm charts
- **[Change Management](CHANGE-MANAGEMENT.md)** - Making safe changes to the repository
- **[Values Hierarchy](VALUES-HIERARCHY.md)** - Understanding configuration inheritance

### 🏗️ Architecture & Decisions

- **[Architectural Decision Records](decisions/)** - Why things are the way they are
  - ADR 001: Use OpenShift (Routes, SCC, native features)
  - ADR 002: Validated Patterns Framework (bootstrap → roles → ApplicationSets)
  - ADR 003: Topology Structure (SNO/Compact/Full roles)
  - ADR 004-008: See [ADR Index](decisions/INDEX.md) for complete list
- **[Deployment Options](deployment/DEPLOYMENT-OPTIONS.md)** - Choose the right deployment pattern
- **[Repository Organization](archive/REPOSITORY-ORGANIZATION-PROPOSAL.md)** - Multi-site strategy

### 🔧 Reference

- **[Available Applications](docs/reference/)** - Full application catalog
- **[TrueNAS Configuration](docs/reference/truenas-csi-configuration.md)** - Storage setup
- **[Chart Exceptions](docs/CHART-EXCEPTIONS.md)** - Documented deviations from standards

### 🚨 Troubleshooting

- **[OpenShift Connectivity](docs/troubleshooting/openshift-connectivity.md)**
- **[TrueNAS CSI](docs/troubleshooting/truenas-csi.md)**
- **[NFS Storage](docs/troubleshooting/nfs-storage.md)**
- **[Keepalived](docs/troubleshooting/keepalived.md)**

## Available Applications

### AI/ML Applications (`charts/ai/`)

- **LiteLLM**: Unified API proxy for managing multiple LLM providers
- **Ollama**: Local large language model runtime
- **Open WebUI**: User-friendly web interface for interacting with LLMs

### Platform Infrastructure Applications (`charts/platform/`)

- **Certificates**: Certificate management for cluster TLS
- **Custom Error Pages**: Custom error pages for ingress/routes
- **Gatus**: Service monitoring and health checks with status page
- **Generic Device Plugin**: Kubernetes device plugin for custom resources
- **Goldilocks**: VPA (Vertical Pod Autoscaler) recommendations dashboard
- **K10 Kasten Operator**: Backup and disaster recovery operator
- **Keepalived Operator**: Virtual IP management for high availability
- **OpenShift NFD**: Node Feature Discovery for hardware detection
- **System Reservation**: Resource reservation for system workloads
- **Vertical Pod Autoscaler**: Automatic container resource recommendations
- **MetalLB**: LoadBalancer implementation for bare metal clusters
- **External Secrets Operator**: Kubernetes operator for external secret management
- **GPU Operators**: AMD and Intel GPU operators for hardware acceleration

### Home Automation Applications (`charts/home-automation/`)

- **EMQX Operator**: MQTT broker operator for IoT messaging
- **Home Assistant**: Open-source home automation platform
- **Node-RED**: Flow-based development tool for IoT
- **Zwavejs2MQTT**: Z-Wave to MQTT gateway

### Infrastructure Applications (`charts/infrastructure/`)

- **Advanced Cluster Management**: Multi-cluster management for OpenShift
- **Intel GPU Operator**: Intel GPU support for AI/ML workloads
- **Multicluster Engine**: Engine for managing multiple clusters

### Media Applications (`charts/media/`)

- **Bazarr**: Subtitle management for movies and TV shows
- **FlareSolverr**: Cloudflare proxy solver for web scraping
- **Gaps**: Tool for finding missing movies in collections
- **Huntarr**: Wanted movie management and automation
- **Jellyfin**: Free software media system (Plex alternative)
- **Jellyseerr**: Media request management for Jellyfin
- **Kapowarr**: Comic book collection management
- **Kavita**: Digital library server and comic/book reader
- **Lidarr**: Music collection management and automation
- **Metube**: Web-based YouTube downloader
- **Overseerr**: Media request management for Plex users
- **Pinchflat**: YouTube channel archiver and downloader
- **Plex**: Media server for streaming movies, TV shows, and music
- **Posterizarr**: Automated poster management for media libraries
- **Prowlarr**: Indexer management for \*arr applications
- **Radarr**: Movie collection management and automation
- **Readarr**: Book and audiobook collection management
- **Recyclarr**: TRaSH Guides automation for \*arr applications
- **SABnzbd**: Usenet newsreader and downloader
- **Sonarr**: TV series collection management and automation
- **Tautulli**: Plex media server analytics and monitoring

### Productivity Applications (`charts/productivity/`)

- **Bookmarks**: Web bookmark management service
- **CyberChef**: Data manipulation and analysis toolkit
- **Excalidraw**: Collaborative whiteboard and diagramming tool
- **IT-Tools**: Collection of handy IT utilities and converters
- **Startpunkt**: Customizable homepage and application dashboard
- **Terraform Enterprise**: Private Terraform Cloud alternative

### Radio Applications (`charts/radio/`)

- **ADSB**: ADS-B aircraft tracking receiver and aggregator

### Security Applications (`charts/security/`)

- **External Secrets Operator**: Kubernetes operator for managing external secrets from providers like Infisical, AWS Secrets Manager, etc.

### Storage Applications (`charts/storage/`)

- **Synology CSI**: CSI driver for Synology NAS storage (iSCSI/NFS)
- **TrueNAS CSI**: CSI driver for TrueNAS storage (iSCSI/NFS)

### Tweaks/Optimizations (`charts/tweaks/`)

- **Disable Master Secondary Interfaces**: Removes unused network interfaces on control plane nodes
- **Disable Worker Secondary Interfaces**: Removes unused network interfaces on worker nodes
- **Snapshot Finalizer Remover**: Cleanup job for stuck VolumeSnapshot finalizers

## Getting Started

See the **[Cluster Bootstrap Guide](operations/CLUSTER-BOOTSTRAP.md)** for complete step-by-step instructions.

Quick start:

1. Install OpenShift GitOps operator
2. Grant Argo CD cluster-admin permissions
3. Create the cluster Application pointing to your chosen role
4. Monitor ApplicationSet and Application creation
5. Access apps via Routes: `<app-name>.apps.<cluster-name>.<domain>`

## Configuration

### Cluster Configuration

Configuration is managed via Helm values in `roles/<cluster-name>/values.yaml`:

```yaml
config:
  cluster:
    top_level_domain: roybales.com
    name: sno
    admin_email: admin@example.com
    timezone: America/New_York
    storage:
      truenas:
        zfs:
          datasetParentName: "volume1/iscsi/sno/vols"
        iscsi:
          namePrefix: "sno-"
      config:
        storageClassName: truenas-iscsi
      media:
        nfs:
          server: truenas.example.com
          path: /mnt/volume1/media

  plex:
    network:
      ip: 192.168.1.200

  certificates:
    letsencrypt:
      issuer: production

  externalSecrets:
    secret: infisical-auth-secret
    infisical:
      projectSlug: hub
      environmentSlug: prod
```

### Enabling/Disabling Applications

Edit the ApplicationSet templates in `roles/<cluster-name>/templates/` to control which apps are deployed:

```yaml
# roles/sno/templates/ai.yaml
spec:
  generators:
    - list:
        elements:
          - name: litellm # Enabled
            group: ai
          - name: open-webui # Enabled
            group: ai
          # - name: jupyter-hub  # Disabled (commented out)
          #   group: ai
```

## OpenShift Integration Features

### Networking

- **Routes**: Automatic HTTPS routes with edge termination
- **Services**: ClusterIP services for internal communication

### UI Integration

- **Console Links**: Applications appear in OpenShift console menus
- **Cluster Homepage**: Startpunkt is used as the cluster homepage and every application is listed there

### Storage

- **Flexible storage**: Uses the default cluster CSI driver unless a different one is specified
- **NFS integration**: Shared storage for media applications via NFS
- **Backup annotations**: Kasten backup integration

## Customization

### Adding a New Application

See **[Adding Applications Guide](.github/instructions/adding-application-checklist.md)** for detailed instructions.

Quick steps:

1. Choose the appropriate functional group (ai, media, home-automation, productivity, etc.)
2. Create a new Helm chart in `charts/applications/<domain>/<app>/`
   - Include `crds/` directory if the app requires Custom Resource Definitions (operators, controllers)
   - CRDs are installed automatically before other resources
3. Add the app to ApplicationSet generators in **ALL** cluster roles:
   - `roles/sno/templates/<group>.yaml`
   - `roles/hub/templates/<group>.yaml`
   - `roles/test/templates/<group>.yaml`
4. Commit and push - Argo CD will sync automatically

**Scaffold script available:**

```bash
./scripts/chart-tools/scaffold-new-chart.sh
```

### Custom Resource Definitions (CRDs)

For applications that require CRDs (operators, custom controllers):

**Chart Structure:**

```text
charts/applications/<domain>/<app>/
├── Chart.yaml
├── values.yaml
├── crds/                          # ← CRDs go here
│   └── *.crd.yaml                 # Pure YAML, no Helm templating
└── templates/
    ├── deployment.yaml
    ├── custom-resource.yaml       # Resources using the CRDs
    └── ...
```

**Key Points:**

- CRDs **must** be in the `crds/` directory, not `templates/`
- Helm installs CRDs **before** any other resources automatically
- CRDs do **not** support Helm templating (`{{ }}` syntax)
- CRDs do **not** respect sync-wave annotations
- Examples: MetalLB, EMQX Operator, cert-manager

See the [CRD Management section](.github/copilot-instructions.md#crd-management-best-practices) for detailed guidelines.

### Adding a New ApplicationSet Category

To create an entirely new functional group (rare):

1. Create ApplicationSet templates in ALL cluster roles:
   - `roles/sno/templates/<category>.yaml`
   - `roles/hub/templates/<category>.yaml`
   - `roles/test/templates/<category>.yaml`
2. Follow the existing pattern with appropriate sync-wave annotation:
   - Wave 0: Security/secrets management
   - Wave 50: Storage providers
   - Wave 100: Applications
   - Wave 200: Tweaks and optimizations
3. Create corresponding subdirectory in `charts/<category>/`

## Scripts and Tools

### VPA Goldilocks Reporter

A comprehensive Python script for analyzing VPA (Vertical Pod Autoscaler) recommendations from Goldilocks and generating detailed resource configuration reports.

**Features:**

- Multiple output formats: Console, JSON, YAML, HTML, kubectl patches
- Namespace filtering and comprehensive resource analysis
- Comparison between current and recommended configurations
- Ready-to-use kubectl patch commands for applying recommendations

**Usage:**

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Generate console report
./scripts/reporting/vpa-goldilocks-reporter.py

# Generate HTML report for media namespace
./scripts/reporting/vpa-goldilocks-reporter.py --format html --namespace media --output report.html

# Generate kubectl patches
./scripts/reporting/vpa-goldilocks-reporter.py --format kubectl --output apply-recommendations.sh
```

See [`scripts/README-vpa-goldilocks-reporter.md`](scripts/README-vpa-goldilocks-reporter.md) for complete documentation.

## Maintenance

- **Automated Updates**: Renovate monitors and updates application image versions
- **Sync Policy**: Applications are configured with automated sync (prune + selfHeal)
- **Health Monitoring**: Gatus provides real-time application health checks
- **Resource Optimization**: Goldilocks/VPA provides resource recommendations

## Documentation

### Getting Started

- **[Cluster Bootstrap](operations/CLUSTER-BOOTSTRAP.md)**: Complete cluster setup instructions
- **[Architecture Guide](../.github/copilot-instructions.md)**: Detailed architecture and patterns
- **[Adding Applications](instructions/adding-an-application-checklist.md)**: Step-by-step guide for adding new apps

### Development & Maintenance

- **[Change Management Guide](docs/CHANGE-MANAGEMENT.md)**: Checklists for moving charts, editing templates, adding apps
- **[Change Management Quick Reference](docs/CHANGE-MANAGEMENT-QUICK-REF.md)**: Quick lookup for common tasks
- **[Chart Standards](docs/CHART-STANDARDS.md)**: Application chart requirements and best practices
- **[Chart Exceptions](docs/CHART-EXCEPTIONS.md)**: Documented deviations from standards

### Reference Documentation

- **[Application Management Quick Ref](docs/APP-MANAGEMENT-QUICK-REF.md)**: Complete app inventory and enable/disable guide
- **[Values Hierarchy](docs/VALUES-HIERARCHY.md)**: Multi-layer configuration structure
- **[AI Stack Recommendations](docs/ai-stack/recommended-tools.md)**: Recommended AI/ML tools to add
- **[Architectural Decision Records](docs/decisions/)**: ADR 001 (OpenShift), ADR 002 (Validated Patterns), ADR 003 (Topology)

### Troubleshooting

- **[TrueNAS CSI Troubleshooting](docs/troubleshooting/truenas-csi.md)**: Storage troubleshooting guide
- **[OpenShift Connectivity](docs/troubleshooting/openshift-connectivity.md)**: Network and cluster access issues
- **[Keepalived Issues](docs/troubleshooting/keepalived.md)**: Load balancer troubleshooting

## Developer Notes

### Validations

Run validations using Task:

```bash
# Run all validations (ADR checks and Helm template/lint)
task validate:all

# Run only Helm validations
task validate:helm

# Run ADR validation
task validate:adr
```

The CI pipeline runs `validate:all` on pushes and PRs.

### Pre-commit Hooks

Local hooks run ADR validation and Helm validation/lint:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Ensure helm and task are in your PATH
which helm task
```

### Tools Required

- `helm` - Chart templating and linting
- `task` - Task runner
- `oc` or `kubectl` - Kubernetes CLI
- `python3` - For scripts (with requirements.txt installed)
