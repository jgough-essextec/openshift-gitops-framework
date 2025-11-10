# Architectural Decision Records (ADR) Index

This directory contains all Architectural Decision Records for the argo-apps repository using the MADR (Markdown Architectural Decision Records) format.

## Active ADRs

| ADR                                                           | Title                              | Status      | Date       | Summary                                                                       |
| ------------------------------------------------------------- | ---------------------------------- | ----------- | ---------- | ----------------------------------------------------------------------------- |
| [0000](./0000-use-markdown-architectural-decision-records.md) | Use Markdown ADRs                  | Accepted    | 2024       | Use MADR 4.0.0 format for all ADRs                                            |
| [0001](./0001-use-openshift.md)                               | Use OpenShift                      | Accepted    | 2025-09-11 | Use OpenShift as the reference Kubernetes platform                            |
| [002](./002-validated-patterns-framework-migration.md)        | Validated Patterns Framework       | In Progress | 2024-11-05 | Adopt Red Hat Validated Patterns three-layer architecture                     |
| [003](./003-simplify-cluster-topology-structure.md)           | Topology Structure                 | Proposed    | 2025-11-06 | Simplify cluster topology with roles (SNO/Compact/Full)                       |
| [004](./004-application-source-selection-priority.md)         | Application Source Selection       | Accepted    | 2025-11-07 | Operator-first, source-priority pattern for applications                      |
| [005](./005-values-hierarchy-pattern.md)                      | Values Hierarchy Pattern           | Accepted    | 2025-11-07 | Four-level values hierarchy (Global → Set → Topology → Cluster)               |
| [006](./006-chart-standards-and-security.md)                  | Chart Standards & Security         | Accepted    | 2025-11-07 | OpenShift-first chart standards with restricted SCC compliance                |
| [007](./007-application-domain-organization.md)               | Application Domain Organization    | Accepted    | 2025-11-07 | Functional domains (AI, Media, Home Automation, Productivity, Infrastructure) |
| [008](./008-multi-cluster-management-strategy.md)             | Multi-Cluster Strategy             | Accepted    | 2025-11-07 | Hub-and-spoke with ACM, GitOps pull model                                     |
| [009](./009-use-trash-guides-directory-structure.md)          | TRaSH-Guides Directory Structure   | Accepted    | 2025-09-11 | Use TRaSH-Guides directory layout for media applications                      |
| [010](./010-standardize-data-mounts-for-media-containers.md)  | Standardize Media Container Mounts | Accepted    | 2025-09-11 | Common `/data` mount across all media containers for hardlink efficiency      |
| [0011](./0011-use-external-secrets-operator.md)               | Use External Secrets Operator      | Accepted    | 2025-11-08 | ESO for GitOps-compatible secret management with multi-backend support        |
| [0012](./0012-use-gatus-for-health-monitoring.md)             | Use Gatus for Health Monitoring    | Accepted    | 2025-11-08 | Lightweight health dashboard with GitOps-managed checks                       |
| [0013](./0013-use-vpa-goldilocks-for-resource-sizing.md)      | Use VPA+Goldilocks for Resources   | Accepted    | 2025-11-08 | VPA in recommendation-only mode with Goldilocks dashboard                     |

## ADR Status Definitions

- **Proposed:** ADR is under discussion, not yet implemented
- **Accepted:** ADR is approved and being actively implemented
- **In Progress:** ADR is partially implemented, work ongoing
- **Superseded:** ADR has been replaced by a newer decision
- **Deprecated:** ADR is no longer relevant but kept for historical context
- **Rejected:** ADR was considered but not adopted

## Quick Navigation

### By Topic

**Platform & Infrastructure:**

- [0001: Use OpenShift](./0001-use-openshift.md)
- [002: Validated Patterns Framework](./002-validated-patterns-framework-migration.md)
- [003: Topology Structure](./003-simplify-cluster-topology-structure.md)
- [008: Multi-Cluster Strategy](./008-multi-cluster-management-strategy.md)
- [0011: Use External Secrets Operator](./0011-use-external-secrets-operator.md)
- [0012: Use Gatus for Health Monitoring](./0012-use-gatus-for-health-monitoring.md)
- [0013: Use VPA+Goldilocks for Resource Sizing](./0013-use-vpa-goldilocks-for-resource-sizing.md)

**Application Management:**

- [004: Application Source Selection](./004-application-source-selection-priority.md)
- [007: Application Domain Organization](./007-application-domain-organization.md)
- [009: TRaSH-Guides Directory Structure](./009-use-trash-guides-directory-structure.md) _(Media domain)_
- [010: Standardize Media Container Mounts](./010-standardize-data-mounts-for-media-containers.md) _(Media domain)_

**Configuration & Standards:**

- [005: Values Hierarchy Pattern](./005-values-hierarchy-pattern.md)
- [006: Chart Standards & Security](./006-chart-standards-and-security.md)

**Process & Documentation:**

- [0000: Use Markdown ADRs](./0000-use-markdown-architectural-decision-records.md)

## Key Decisions Summary

### ADR 0001: Use OpenShift

**Decision:** Use OpenShift as the reference Kubernetes platform

**Why:** Aligns with day-to-day work, provides enterprise-grade features (Routes, SCC, operators)

**Impact:** Charts must work under OpenShift restricted SCC, prefer Routes over Ingress

---

### ADR 002: Validated Patterns Framework

**Decision:** Adopt three-layer architecture: Bootstrap → Roles → ApplicationSets → Apps

**Why:** Eliminates duplication, scales better, clear separation of concerns

**Impact:** Charts organized hierarchically, values cascade through layers

---

### ADR 003: Topology Structure

**Decision:** Three topology roles (SNO/Compact/Full) with topology-specific resource configurations

**Why:** Node count determines HA strategy, replica counts, PDB settings

**Impact:** Topology-aware values in `clusters/topologies/`, roles define deployment patterns

---

### ADR 004: Application Source Selection

**Decision:** Operator-first pattern: Operators > Helm Charts > Custom, Official > Verified > CNCF > Community

**Why:** Operators provide better lifecycle management, official sources more maintainable

**Impact:** Check OperatorHub.io first, document source selection rationale

---

### ADR 005: Values Hierarchy Pattern

**Decision:** Four-level hierarchy: Global → Cluster Set → Topology → Individual Cluster

**Why:** Eliminates 80%+ duplication, clear precedence, infrastructure separation

**Impact:** Values files in `clusters/` subdirectories, Helm merge order critical

---

### ADR 006: Chart Standards & Security

**Decision:** OpenShift-first with restricted SCC compliance, namespace-scoped resources only

**Why:** Security by default, portability, clear platform/app boundaries

**Impact:** All charts must pass security audit, CRDs in `/crds/`, Routes by default

---

### ADR 007: Application Domain Organization

**Decision:** Five functional domains: AI, Media, Home Automation, Productivity, Infrastructure

**Why:** Aligns with user mental models, manageable ApplicationSet sizes, domain-level control

**Impact:** Master ApplicationSet per domain, domain-specific documentation

---

### ADR 008: Multi-Cluster Strategy

**Decision:** Hub-and-spoke with ACM/MCE, GitOps pull model (each cluster autonomous)

**Why:** Centralized observability, cluster autonomy, scales to 10+ clusters

**Impact:** Hub cluster required, local GitOps per managed cluster, cluster registration process

---

### ADR 0011: Use External Secrets Operator

**Decision:** Use External Secrets Operator (ESO) for secret management with multi-backend support

**Why:** GitOps-compatible secret management, multi-backend flexibility (Infisical, AWS, Azure, Vault), separation of concerns

**Impact:** Secrets stored externally, ExternalSecret CRs in Git, sync-wave 0 for security, ESO deployed as platform component

---

### ADR 0012: Use Gatus for Health Monitoring

**Decision:** Use Gatus for lightweight application health monitoring with GitOps-managed checks

**Why:** Application-focused monitoring, health checks as code, built-in alerting, simple dashboard

**Impact:** Health checks defined in app chart values, Gatus deployed as platform component, complements cluster monitoring

---

### ADR 0013: Use VPA+Goldilocks for Resource Sizing

**Decision:** Use Vertical Pod Autoscaler (VPA) in recommendation-only mode with Goldilocks dashboard

**Why:** Data-driven resource sizing, prevents over/under-provisioning, visual recommendations, safe non-automated mode

**Impact:** VPA deployed as platform component, Goldilocks namespace labels, operator reviews recommendations periodically

---

## Creating New ADRs

### When to Create an ADR

Create an ADR when making decisions about:

- Platform architecture or major refactoring
- Significant changes to application patterns
- New frameworks or major dependencies
- Security or compliance requirements
- Multi-cluster or infrastructure changes
- Standards that affect multiple components

### ADR Template

Use `template.md` in this directory as a starting point:

```bash
cp docs/decisions/template.md docs/decisions/00X-descriptive-title.md
```

### Required Sections

1. **Metadata:** Status, date, decision-makers, consulted, informed
2. **Context and Problem Statement:** What problem are we solving?
3. **Decision Drivers:** What factors influenced the decision?
4. **Considered Options:** What alternatives did we evaluate?
5. **Decision Outcome:** What did we choose and why?
6. **Consequences:** Good, bad, and neutral outcomes
7. **Confirmation:** How do we verify the decision is working?
8. **Pros and Cons:** Detailed comparison of options

### ADR Validation

Run the validation script before committing:

```bash
./docs/decisions/validate-adr.sh docs/decisions/00X-your-new-adr.md
```

## Related Documentation

- **Change Management:** `docs/CHANGE-MANAGEMENT.md` - How to apply ADRs
- **Chart Standards:** `docs/CHART-STANDARDS.md` - Implementation of ADR 006
- **Values Hierarchy:** `docs/VALUES-HIERARCHY.md` - Implementation of ADR 005
- **Configuration Guide:** `docs/CONFIGURATION-GUIDE.md` - Implementation of ADR 002, 003, 005
- **Kubeconfig Management:** `docs/operations/KUBECONFIG-MANAGEMENT.md` - Implementation of ADR 008

## References

- **MADR:** https://adr.github.io/madr/
- **ADR Organization:** https://github.com/joelparkerhenderson/architecture_decision_record
- **Red Hat Validated Patterns:** https://validatedpatterns.io/
- **OpenShift Documentation:** https://docs.openshift.com/

## Maintenance

### Updating ADRs

- **Minor Clarifications:** Edit ADR directly, note in "Notes" section
- **Status Changes:** Update status field and date
- **Superseding ADRs:** Create new ADR, link from old one, mark old as "Superseded"

### ADR Retirement

Don't delete ADRs. Instead:

1. Mark status as "Superseded" or "Deprecated"
2. Link to replacement ADR
3. Keep for historical context

---

**Last Updated:** 2025-11-08
