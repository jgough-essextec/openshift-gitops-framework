# Documentation Index

Complete guide to all documentation in the argo-apps repository.

## 📚 Quick Navigation

- [Getting Started](#getting-started)
- [Architecture & Standards](#architecture--standards)
- [Instructions & Workflows](#instructions--workflows)
- [Deployment Options](#deployment-options)
- [Operations](#operations)
- [Reference Materials](#reference-materials)
- [Domain-Specific](#domain-specific)
- [Troubleshooting](#troubleshooting)
- [Scripts & Tools](#scripts--tools)
- [Decisions & Planning](#decisions--planning)

---

## Getting Started

Start here for initial setup and understanding the framework.

| Document                                                                | Description                             |
| ----------------------------------------------------------------------- | --------------------------------------- |
| [Getting Started Guide](../GETTING-STARTED.md)                          | Initial setup and first steps           |
| [README](../README.md)                                                  | Repository overview and quick links     |
| [Deployment Options](./deployment/DEPLOYMENT-OPTIONS.md)                | Choose your deployment pattern          |
| [Single Cluster Quick Start](./deployment/single-cluster-quickstart.md) | Deploy a single OpenShift cluster       |
| [Multi-Cluster Quick Start](./deployment/multi-cluster-quickstart.md)   | Deploy multiple clusters without ACM    |
| [ACM Quick Start](./deployment/acm-quickstart.md)                       | Deploy with Advanced Cluster Management |
| [Multi-Site Quick Start](./deployment/multi-site-quickstart.md)         | Deploy across multiple sites with ACM   |

## Architecture & Standards

Understand the architecture and standards that govern this repository.

### Core Architecture

| Document                                                              | Description                                |
| --------------------------------------------------------------------- | ------------------------------------------ |
| [Detailed Overview](./DETAILED-OVERVIEW.md)                           | Comprehensive architecture documentation   |
| [Architecture Quick Reference](./reference/ARCHITECTURE-QUICK-REF.md) | One-page visual architecture guide         |
| [Values Hierarchy](./VALUES-HIERARCHY.md)                             | Configuration inheritance and precedence   |
| [Chart Standards](./CHART-STANDARDS.md)                               | **REQUIRED** standards for all Helm charts |
| [Chart Exceptions](./CHART-EXCEPTIONS.md)                             | Documented deviations from standards       |

### Configuration Management

| Document                                                 | Description                              |
| -------------------------------------------------------- | ---------------------------------------- |
| [Configuration Guide](./CONFIGURATION-GUIDE.md)          | Template vs user-specific configurations |
| [Values Migration Guide](../MIGRATION-VALUES-FILES.md)   | Migrating configuration between versions |
| [Values Secret Template](../values-secret.yaml.template) | Template for secret values               |

## Instructions & Workflows

Step-by-step instructions for common tasks.

### Application Management

| Document                                                                   | Description                             |
| -------------------------------------------------------------------------- | --------------------------------------- |
| [Adding an Application](./instructions/adding-application.md)              | Core workflow for adding new apps       |
| [Application Checklist](./instructions/adding-an-application-checklist.md) | **REQUIRED** checklist for new apps     |
| [Adding a Domain](./instructions/adding-a-new-domain.md)                   | Create new application domains          |
| [App Management Quick Reference](./APP-MANAGEMENT-QUICK-REF.md)            | Quick commands and patterns             |
| [Preferred Sources](./reference/PREFERRED-SOURCES.md)                      | Where to find application charts/images |

### Domain-Specific Instructions

| Domain          | Document                                                                         |
| --------------- | -------------------------------------------------------------------------------- |
| AI              | [AI Domain Instructions](./instructions/domains/ai.md)                           |
| Media           | [Media Domain Instructions](./instructions/domains/media.md)                     |
| Home Automation | [Home Automation Domain Instructions](./instructions/domains/home-automation.md) |
| Productivity    | [Productivity Domain Instructions](./instructions/domains/productivity.md)       |
| Infrastructure  | [Infrastructure Domain Instructions](./instructions/domains/infrastructure.md)   |

### Change Management

| Document                                                              | Description                     |
| --------------------------------------------------------------------- | ------------------------------- |
| [Change Management Guide](./CHANGE-MANAGEMENT.md)                     | Checklists for all change types |
| [Simplification Recommendations](./SIMPLIFICATION-RECOMMENDATIONS.md) | Suggested improvements          |

## Deployment Options

Choose and implement your deployment pattern.

| Pattern                | Document                                                 | Use When                                 |
| ---------------------- | -------------------------------------------------------- | ---------------------------------------- |
| Single Cluster         | [Quick Start](./deployment/single-cluster-quickstart.md) | Testing, learning, or single environment |
| Multi-Cluster (No ACM) | [Quick Start](./deployment/multi-cluster-quickstart.md)  | Few clusters, simple management          |
| Multi-Cluster (ACM)    | [Quick Start](./deployment/acm-quickstart.md)            | Many clusters, centralized control       |
| Multi-Site             | [Quick Start](./deployment/multi-site-quickstart.md)     | Geographic distribution, DR requirements |

### Advanced Cluster Management

| Document                                                               | Description                     |
| ---------------------------------------------------------------------- | ------------------------------- |
| [ACM Getting Started](./ACM-GETTING-STARTED.md)                        | Introduction to ACM concepts    |
| [ACM Platform Deployment](./operations/acm/ACM-PLATFORM-DEPLOYMENT.md) | ACM platform setup instructions |
| [ACM Organization](./operations/acm/ACM-ORGANIZATION.md)               | Organizing clusters with ACM    |
| [ACM Quick Start](./operations/acm/QUICK-START.md)                     | 5-minute ACM setup              |

## Operations

Day-to-day operational guides and tools.

### Cluster Operations

| Document                                                             | Description                         |
| -------------------------------------------------------------------- | ----------------------------------- |
| [Cluster Bootstrap](./operations/CLUSTER-BOOTSTRAP.md)               | Step-by-step cluster setup          |
| [Kubeconfig Management](./operations/KUBECONFIG-MANAGEMENT.md)       | Managing cluster access credentials |
| [Cluster Cleanup](../scripts/README-cleanup-cluster.md)              | Safe cluster teardown procedures    |
| [Multi-Cluster Management](./operations/MULTI-CLUSTER-MANAGEMENT.md) | Working with multiple clusters      |

### Monitoring & Maintenance

| Document                                                                  | Description                     |
| ------------------------------------------------------------------------- | ------------------------------- |
| [VPA & Goldilocks Reporter](../scripts/README-vpa-goldilocks-reporter.md) | Resource recommendation reports |
| [Kasten Excluded Apps](../scripts/README-kasten-excluded-apps.md)         | Backup exclusion management     |
| [Custom Error Pages](../scripts/README-update-error-pages.md)             | Update custom error pages       |

## Reference Materials

Technical references and lookup guides.

### Application References

| Document                                                                      | Description                                |
| ----------------------------------------------------------------------------- | ------------------------------------------ |
| [Preferred Sources](./reference/PREFERRED-SOURCES.md)                         | Official repositories and registries       |
| [Application Sources Quick Ref](./reference/APPLICATION-SOURCES-QUICK-REF.md) | One-page search reference (print/bookmark) |
| [AI Stack Documentation](./ai-stack/)                                         | AI/ML application documentation            |

### API & CLI References

| Document                                            | Description                |
| --------------------------------------------------- | -------------------------- |
| [Pattern Metadata Schema](../pattern-metadata.yaml) | Pattern metadata structure |
| [Taskfile Reference](../Taskfile.yaml)              | Available automation tasks |

### Reports

| Directory              | Contents                                |
| ---------------------- | --------------------------------------- |
| [reports/](./reports/) | Generated compliance and status reports |

## Domain-Specific

Application domain documentation and guides.

| Domain              | Description                                      | Document                     |
| ------------------- | ------------------------------------------------ | ---------------------------- |
| **AI**              | AI/ML applications (LiteLLM, Ollama, Open WebUI) | [AI Stack Docs](./ai-stack/) |
| **Media**           | Media management (Plex, Sonarr, Radarr, etc.)    | Coming soon                  |
| **Home Automation** | IoT and smart home (Home Assistant, Node-RED)    | Coming soon                  |
| **Productivity**    | Productivity tools (Bookmarks, Excalidraw, etc.) | Coming soon                  |
| **Infrastructure**  | Core infrastructure (Paperless, ADS-B, etc.)     | Coming soon                  |

## Troubleshooting

Diagnose and fix common issues.

| Directory                              | Contents                        |
| -------------------------------------- | ------------------------------- |
| [troubleshooting/](./troubleshooting/) | Troubleshooting guides by topic |

### Common Issues

- Application won't sync
- Route/Ingress issues
- Storage problems
- External Secrets failures
- Multi-cluster context errors

## Scripts & Tools

Automation and utility scripts.

### Main Scripts Documentation

| Script              | Purpose                          | Documentation                                                                             |
| ------------------- | -------------------------------- | ----------------------------------------------------------------------------------------- |
| **Chart Tools**     | Chart scaffolding and validation | [scripts/README.md](../scripts/README.md)                                                 |
| **Audit Tools**     | Chart standards compliance       | [scripts/audit/README.md](../scripts/audit/README.md)                                     |
| **Cleanup Tools**   | Cluster resource cleanup         | [scripts/README-cleanup-cluster.md](../scripts/README-cleanup-cluster.md)                 |
| **Icon Tools**      | Icon validation and management   | [scripts/README.md](../scripts/README.md)                                                 |
| **Reporting Tools** | VPA/Goldilocks reporting         | [scripts/README-vpa-goldilocks-reporter.md](../scripts/README-vpa-goldilocks-reporter.md) |

### Script Categories

| Category               | Location                      | Purpose                       |
| ---------------------- | ----------------------------- | ----------------------------- |
| **Audit**              | `scripts/audit/`              | Chart standards auditing      |
| **Chart Tools**        | `scripts/chart-tools/`        | Chart scaffolding, updates    |
| **Cluster Operations** | `scripts/cluster-operations/` | Cluster cleanup, management   |
| **Icon Tools**         | `scripts/icon-tools/`         | Icon validation               |
| **Maintenance**        | `scripts/maintenance/`        | Ongoing maintenance tasks     |
| **Reporting**          | `scripts/reporting/`          | Status and compliance reports |

## Decisions & Planning

Architectural decisions and future planning.

### Architectural Decision Records (ADRs)

**📖 [Complete ADR Index](./decisions/INDEX.md)** - All architectural decisions with summaries

**Key ADRs:**

| ADR                                                                     | Title                           | Status      | Category       |
| ----------------------------------------------------------------------- | ------------------------------- | ----------- | -------------- |
| [0000](./decisions/0000-use-markdown-architectural-decision-records.md) | Use Markdown ADRs               | Accepted    | Process        |
| [0001](./decisions/0001-use-openshift.md)                               | Use OpenShift                   | Accepted    | Platform       |
| [002](./decisions/002-validated-patterns-framework-migration.md)        | Validated Patterns Framework    | In Progress | Architecture   |
| [003](./decisions/003-simplify-cluster-topology-structure.md)           | Topology Structure              | Proposed    | Infrastructure |
| [004](./decisions/004-application-source-selection-priority.md)         | Application Source Selection    | Accepted    | Applications   |
| [005](./decisions/005-values-hierarchy-pattern.md)                      | Values Hierarchy Pattern        | Accepted    | Configuration  |
| [006](./decisions/006-chart-standards-and-security.md)                  | Chart Standards & Security      | Accepted    | Standards      |
| [007](./decisions/007-application-domain-organization.md)               | Application Domain Organization | Accepted    | Architecture   |
| [008](./decisions/008-multi-cluster-management-strategy.md)             | Multi-Cluster Strategy          | Accepted    | Multi-Cluster  |

### Planning & TODO

| Document                      | Description                                 |
| ----------------------------- | ------------------------------------------- |
| [TODO List](./TODO.md)        | Planned improvements and features           |
| [Known Gaps](./KNOWN-GAPS.md) | Identified limitations and missing features |

## Examples

| Directory                | Contents                             |
| ------------------------ | ------------------------------------ |
| [examples/](./examples/) | Example configurations and use cases |

## Archive

| Directory              | Contents                               |
| ---------------------- | -------------------------------------- |
| [archive/](./archive/) | Deprecated or historical documentation |

---

## Documentation Standards

### For Contributors

When creating new documentation:

1. **Add to this index** - Ensure new documents are listed here
2. **Link from related docs** - Create cross-references
3. **Follow naming conventions** - Use UPPERCASE-WITH-DASHES.md for guides
4. **Include metadata** - Date, author, related docs
5. **Update copilot instructions** - Add to `.github/copilot-instructions.md`

### Document Types

- **Guides** - Step-by-step instructions (GETTING-STARTED.md)
- **References** - Lookup information (CHART-STANDARDS.md)
- **Checklists** - Verification lists (adding-an-application-checklist.md)
- **Decisions** - ADRs in decisions/ directory
- **Troubleshooting** - Problem-solution format

---

## Quick Links by Role

### I'm a Developer

- [Chart Standards](./CHART-STANDARDS.md)
- [Adding an Application Checklist](./instructions/adding-an-application-checklist.md)
- [Change Management Guide](./CHANGE-MANAGEMENT.md)
- [Preferred Sources](./reference/PREFERRED-SOURCES.md)

### I'm an Operator

- [Cluster Operations](./operations/)
- [Troubleshooting](./troubleshooting/)
- [VPA Reporter](../scripts/README-vpa-goldilocks-reporter.md)
- [Cluster Cleanup](../scripts/README-cleanup-cluster.md)

### I'm Getting Started

- [Getting Started Guide](../GETTING-STARTED.md)
- [Deployment Options](./deployment/DEPLOYMENT-OPTIONS.md)
- [Single Cluster Quick Start](./deployment/single-cluster-quickstart.md)
- [Detailed Overview](./DETAILED-OVERVIEW.md)

### I'm an Architect

- [Architectural Decisions](./decisions/)
- [ADR Index](./decisions/INDEX.md)
- [Values Hierarchy](./VALUES-HIERARCHY.md)
- [Deployment Options](./deployment/DEPLOYMENT-OPTIONS.md)

---

**Last Updated:** 2025-11-07
**Maintained By:** Repository maintainers
**Feedback:** Open an issue or PR to improve this index
