# Documentation Index

Complete documentation for the OpenShift GitOps repository using the Validated Patterns Framework.

## 🚀 Getting Started

**New to this repository?** Start here:

- **[Quick Start Guide](../GETTING-STARTED.md)** - Get running in 35 minutes (includes Infisical setup)
- **[Cluster Bootstrap](operations/CLUSTER-BOOTSTRAP.md)** - Detailed step-by-step setup
- **[Deployment Options](deployment/DEPLOYMENT-OPTIONS.md)** - Choose your deployment pattern
- **[Values Hierarchy](VALUES-HIERARCHY.md)** - Understanding configuration

## 💻 Development

**Creating and modifying content:**

- **[Chart Standards](CHART-STANDARDS.md)** - Helm chart requirements and best practices
- **[Change Management](CHANGE-MANAGEMENT.md)** - Safe change procedures (includes quick reference)
- **[Adding Applications](../.github/instructions/adding-an-application-checklist.md)** - Complete app addition guide
- **[Chart Exceptions](CHART-EXCEPTIONS.md)** - Documented standards deviations

## 📖 Reference

**Architecture and design decisions:**

- **[Architectural Decision Records](decisions/)** - Design rationale
  - **[ADR Index](decisions/INDEX.md)** - Complete ADR catalog
  - ADR 001: Use OpenShift (Routes, SCC, native features)
  - ADR 002: Validated Patterns Framework (bootstrap → roles → ApplicationSets)
  - ADR 003: Topology Structure (SNO/Compact/Full)
  - ADR 004-008: See [ADR Index](decisions/INDEX.md) for complete list
- **[Detailed Overview](DETAILED-OVERVIEW.md)** - Complete system documentation

### Reference Materials

Located in `reference/`:

- **[TrueNAS CSI Configuration](reference/truenas-csi-configuration.md)** - Storage setup guide
- **[Icons Available](reference/icons-available.md)** - Material Design Icons list
- **[Icons Validation](reference/icons-validation.md)** - Icon requirements
- **[VS Code Helm Configuration](reference/vscode-helm-configuration.md)** - Editor setup

## 🔧 Troubleshooting

**Common issues and solutions:**

Located in `troubleshooting/`:

- **[OpenShift Connectivity](troubleshooting/openshift-connectivity.md)** - Network issues
- **[TrueNAS CSI](troubleshooting/truenas-csi.md)** - Storage driver issues
- **[TrueNAS CSI Quick Fixes](troubleshooting/truenas-csi-quick-fixes.md)** - Common fixes
- **[NFS Storage](troubleshooting/nfs-storage.md)** - NFS-specific issues
- **[Keepalived](troubleshooting/keepalived.md)** - HA operator issues

## 📦 AI/ML Stack

**AI and Machine Learning applications:**

Located in `ai-stack/`:

- **[Recommended Tools](ai-stack/recommended-tools.md)** - AI stack deployment guide

## 📊 Reports & Audits

**Compliance and analysis:**

Located in `reports/`:

- **[Chart Audit Baseline](reports/)** - Chart standards compliance reports

## 🗄️ Archive

**Historical documentation and implementation notes:**

Located in `archive/`:

- App Inventory Implementation - Application catalog update notes
- Change Management Implementation - Framework setup notes
- Chart Standards Implementation - Standards rollout documentation
- Repository Organization Proposal - Multi-site strategy analysis
- Values Rename Documentation - values-sno → values-prod change

---

## Quick Navigation

### By Role

- **Cluster Administrator:** Start with [Quick Start](../GETTING-STARTED.md) → [Cluster Bootstrap](operations/CLUSTER-BOOTSTRAP.md)
- **Developer:** Review [Chart Standards](CHART-STANDARDS.md) → [Adding Applications](instructions/adding-an-application-checklist.md)
- **Troubleshooter:** Check [Troubleshooting](troubleshooting/) section
- **Architect:** Read [ADRs](decisions/) and [Detailed Overview](DETAILED-OVERVIEW.md)

### By Task

- **Deploy new cluster:** [Quick Start](../GETTING-STARTED.md)
- **Add application:** [Adding Applications Checklist](../.github/instructions/adding-an-application-checklist.md)
- **Change configuration:** [Values Hierarchy](VALUES-HIERARCHY.md)
- **Move/reorganize charts:** [Change Management](CHANGE-MANAGEMENT.md)
- **Fix storage issues:** [TrueNAS Troubleshooting](troubleshooting/truenas-csi.md)
- **Understand design:** [ADRs](decisions/)

---

**Need help?** Open an issue or discussion on GitHub.
